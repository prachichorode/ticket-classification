from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from database import get_db_connection
from ml_model import predict_ticket


app = Flask(__name__)

app.secret_key = "ticket-system-v2-secret-key"


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return wrapper


# ============================================================
# ADMIN REQUIRED
# ============================================================

def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            return redirect(url_for("login"))

        if session.get("role") != "Admin":

            flash(
                "Admin access required.",
                "danger"
            )

            return redirect(url_for("dashboard"))

        return f(*args, **kwargs)

    return wrapper


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(url_for("dashboard"))

    return render_template("intro.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            "Customer"
        )

        if not all(
            [
                full_name,
                username,
                email,
                password
            ]
        ):

            flash(
                "Please fill all required fields.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        # Allow all three roles for your college project
        if role not in [
            "Customer",
            "Support Agent",
            "Admin"
        ]:

            role = "Customer"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users
                (
                    full_name,
                    username,
                    email,
                    password,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    full_name,
                    username,
                    email,
                    generate_password_hash(password),
                    role
                )
            )

            conn.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except Exception as e:

            conn.rollback()

            flash(
                f"Registration failed: {e}",
                "danger"
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

            if user and check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["user_id"]

                session["username"] = user["username"]

                session["full_name"] = user["full_name"]

                session["role"] = user["role"]

                flash(
                    "Login successful.",
                    "success"
                )

                return redirect(
                    url_for("dashboard")
                )

            flash(
                "Invalid username or password.",
                "danger"
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        if session["role"] == "Customer":

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(status = 'Open') AS open_count,
                    SUM(status = 'In Progress') AS progress_count,
                    SUM(status = 'Resolved') AS resolved_count
                FROM tickets
                WHERE user_id = %s
                """,
                (
                    session["user_id"],
                )
            )

        else:

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(status = 'Open') AS open_count,
                    SUM(status = 'In Progress') AS progress_count,
                    SUM(status = 'Resolved') AS resolved_count
                FROM tickets
                """
            )

        stats = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS critical_count
            FROM tickets
            WHERE priority = 'Critical'
            """
        )

        stats["critical_count"] = cursor.fetchone()[
            "critical_count"
        ]

        cursor.execute(
            """
            SELECT
                t.ticket_id,
                t.subject,
                t.priority,
                t.status,
                t.created_at,
                c.category_name
            FROM tickets t
            LEFT JOIN categories c
                ON t.category_id = c.category_id
            WHERE
                (
                    %s = 'Customer'
                    AND t.user_id = %s
                )
                OR
                (
                    %s <> 'Customer'
                )
            ORDER BY t.created_at DESC
            LIMIT 5
            """,
            (
                session["role"],
                session["user_id"],
                session["role"]
            )
        )

        recent_tickets = cursor.fetchall()

        return render_template(
            "dashboard.html",
            stats=stats,
            recent_tickets=recent_tickets
        )

    finally:

        cursor.close()
        conn.close()


# ============================================================
# CREATE TICKET
# ============================================================

@app.route(
    "/create-ticket",
    methods=["GET", "POST"]
)
@login_required
def create_ticket():

    if session["role"] != "Customer":

        flash(
            "Only customers can create tickets from this page.",
            "warning"
        )

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        if not subject or not description:

            flash(
                "Subject and description are required.",
                "danger"
            )

            return render_template(
                "create_ticket.html"
            )

        ticket_text = (
            subject
            + " "
            + description
        )

        predicted_category, predicted_priority = predict_ticket(
            ticket_text
        )

        conn = get_db_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT category_id
                FROM categories
                WHERE category_name = %s
                """,
                (
                    predicted_category,
                )
            )

            category_row = cursor.fetchone()

            category_id = (
                category_row[0]
                if category_row
                else None
            )

            cursor.execute(
                """
                INSERT INTO tickets
                (
                    user_id,
                    category_id,
                    subject,
                    description,
                    priority,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'Open'
                )
                """,
                (
                    session["user_id"],
                    category_id,
                    subject,
                    description,
                    predicted_priority
                )
            )

            conn.commit()

            flash(
                "Ticket created. "
                f"AI predicted Category: {predicted_category} | "
                f"Priority: {predicted_priority}",
                "success"
            )

            return redirect(
                url_for("my_tickets")
            )

        except Exception as e:

            conn.rollback()

            flash(
                f"Ticket creation failed: {e}",
                "danger"
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "create_ticket.html"
    )


# ============================================================
# MY TICKETS
# ============================================================

@app.route("/my-tickets")
@login_required
def my_tickets():

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                t.ticket_id,
                t.subject,
                t.description,
                t.priority,
                t.status,
                t.created_at,
                t.updated_at,
                c.category_name
            FROM tickets t
            LEFT JOIN categories c
                ON t.category_id = c.category_id
            WHERE t.user_id = %s
            ORDER BY t.created_at DESC
            """,
            (
                session["user_id"],
            )
        )

        tickets = cursor.fetchall()

        return render_template(
            "my_tickets.html",
            tickets=tickets
        )

    finally:

        cursor.close()
        conn.close()


# ============================================================
# ALL TICKETS
# ============================================================

@app.route("/all-tickets")
@login_required
def all_tickets():

    if session["role"] == "Customer":

        flash(
            "Access denied.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                t.ticket_id,
                u.username,
                u.full_name,
                u.email,
                c.category_name,
                t.subject,
                t.description,
                t.priority,
                t.status,
                t.created_at,
                t.updated_at
            FROM tickets t
            JOIN users u
                ON t.user_id = u.user_id
            LEFT JOIN categories c
                ON t.category_id = c.category_id
            ORDER BY t.created_at DESC
            """
        )

        tickets = cursor.fetchall()

        return render_template(
            "all_tickets.html",
            tickets=tickets
        )

    finally:

        cursor.close()
        conn.close()


# ============================================================
# UPDATE TICKET
# ============================================================

@app.route(
    "/update-ticket/<int:ticket_id>",
    methods=["GET", "POST"]
)
@login_required
def update_ticket(ticket_id):

    # Customer cannot update tickets
    if session["role"] == "Customer":

        flash(
            "Customers cannot update tickets.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        # Get ticket
        cursor.execute(
            """
            SELECT
                t.*,
                u.username,
                u.full_name,
                c.category_name
            FROM tickets t
            JOIN users u
                ON t.user_id = u.user_id
            LEFT JOIN categories c
                ON t.category_id = c.category_id
            WHERE t.ticket_id = %s
            """,
            (
                ticket_id,
            )
        )

        ticket = cursor.fetchone()

        if not ticket:

            flash(
                "Ticket not found.",
                "danger"
            )

            return redirect(
                url_for("all_tickets")
            )

        # UPDATE
        if request.method == "POST":

            new_status = request.form.get(
                "status"
            )

            new_priority = request.form.get(
                "priority"
            )

            remarks = request.form.get(
                "remarks",
                ""
            ).strip()

            allowed_statuses = [
                "Open",
                "In Progress",
                "Resolved",
                "Closed"
            ]

            allowed_priorities = [
                "Low",
                "Medium",
                "High",
                "Critical"
            ]

            if new_status not in allowed_statuses:

                flash(
                    "Invalid status.",
                    "danger"
                )

                return render_template(
                    "update_ticket.html",
                    ticket=ticket,
                    history=[]
                )

            if new_priority not in allowed_priorities:

                flash(
                    "Invalid priority.",
                    "danger"
                )

                return render_template(
                    "update_ticket.html",
                    ticket=ticket,
                    history=[]
                )

            # ------------------------------------------------
            # Update ticket
            # ------------------------------------------------

            cursor.execute(
                """
                UPDATE tickets
                SET
                    status = %s,
                    priority = %s
                WHERE ticket_id = %s
                """,
                (
                    new_status,
                    new_priority,
                    ticket_id
                )
            )

            # IMPORTANT:
            # We do NOT manually insert into ticket_history.
            #
            # Your MySQL trigger:
            # ticket_status_history
            #
            # automatically creates history when status changes.

            conn.commit()

            flash(
                "Ticket updated successfully.",
                "success"
            )

            return redirect(
                url_for("all_tickets")
            )

        # ----------------------------------------------------
        # Get ticket history
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                h.history_id,
                h.old_status,
                h.new_status,
                h.remarks,
                h.changed_at,
                COALESCE(
                    u.username,
                    'System'
                ) AS changed_by_name
            FROM ticket_history h
            LEFT JOIN users u
                ON h.changed_by = u.user_id
            WHERE h.ticket_id = %s
            ORDER BY h.changed_at DESC
            """,
            (
                ticket_id,
            )
        )

        history = cursor.fetchall()

        return render_template(
            "update_ticket.html",
            ticket=ticket,
            history=history
        )

    finally:

        cursor.close()
        conn.close()


# ============================================================
# DELETE TICKET
# ADMIN ONLY
# ============================================================

@app.route(
    "/delete-ticket/<int:ticket_id>",
    methods=["POST"]
)
@admin_required
def delete_ticket(ticket_id):

    conn = get_db_connection()

    cursor = conn.cursor()

    try:

        # Check ticket exists
        cursor.execute(
            """
            SELECT ticket_id
            FROM tickets
            WHERE ticket_id = %s
            """,
            (
                ticket_id,
            )
        )

        ticket = cursor.fetchone()

        if not ticket:

            flash(
                "Ticket not found.",
                "danger"
            )

            return redirect(
                url_for("all_tickets")
            )

        # Delete ticket
        #
        # ticket_history will also be deleted
        # because the foreign key uses ON DELETE CASCADE.

        cursor.execute(
            """
            DELETE FROM tickets
            WHERE ticket_id = %s
            """,
            (
                ticket_id,
            )
        )

        conn.commit()

        flash(
            f"Ticket #{ticket_id} deleted successfully.",
            "success"
        )

    except Exception as e:

        conn.rollback()

        flash(
            f"Delete failed: {e}",
            "danger"
        )

    finally:

        cursor.close()
        conn.close()

    return redirect(
        url_for("all_tickets")
    )


# ============================================================
# DATABASE CONSOLE
# ============================================================

@app.route(
    "/database-console",
    methods=["GET", "POST"]
)
@admin_required
def database_console():

    result = []

    columns = []

    row_count = None

    command = ""

    if request.method == "POST":

        command = request.form.get(
            "sql_command",
            ""
        ).strip()

        if not command:

            flash(
                "Enter an SQL command.",
                "warning"
            )

            return render_template(
                "database_console.html",
                result=result,
                columns=columns,
                row_count=row_count,
                command=command
            )

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(command)

            if cursor.with_rows:

                result = cursor.fetchall()

                columns = (
                    list(result[0].keys())
                    if result
                    else []
                )

                row_count = len(result)

            else:

                conn.commit()

                row_count = cursor.rowcount

            # Save command history
            log_cursor = conn.cursor()

            log_cursor.execute(
                """
                INSERT INTO sql_command_history
                (
                    user_id,
                    sql_command,
                    execution_status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    session["user_id"],
                    command,
                    "SUCCESS"
                )
            )

            conn.commit()

            log_cursor.close()

            flash(
                "SQL command executed successfully.",
                "success"
            )

        except Exception as e:

            conn.rollback()

            try:

                log_cursor = conn.cursor()

                log_cursor.execute(
                    """
                    INSERT INTO sql_command_history
                    (
                        user_id,
                        sql_command,
                        execution_status
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        session["user_id"],
                        command,
                        "FAILED"
                    )
                )

                conn.commit()

                log_cursor.close()

            except Exception:

                conn.rollback()

            flash(
                f"SQL Error: {e}",
                "danger"
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "database_console.html",
        result=result,
        columns=columns,
        row_count=row_count,
        command=command
    )


# ============================================================
# SQL HISTORY
# ============================================================

@app.route("/sql-history")
@admin_required
def sql_history():

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                h.command_id,
                u.username,
                h.sql_command,
                h.execution_status,
                h.executed_at
            FROM sql_command_history h
            JOIN users u
                ON h.user_id = u.user_id
            ORDER BY h.executed_at DESC
            """
        )

        history = cursor.fetchall()

        return render_template(
            "sql_history.html",
            history=history
        )

    finally:

        cursor.close()
        conn.close()


# ============================================================
# ANALYTICS
# ============================================================

@app.route("/analytics")
@login_required
def analytics():

    if session["role"] == "Customer":

        flash(
            "Analytics is available to staff only.",
            "warning"
        )

        return redirect(
            url_for("dashboard")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        # Category statistics
        cursor.execute(
            """
            SELECT
                COALESCE(
                    c.category_name,
                    'Uncategorized'
                ) AS category_name,
                COUNT(*) AS total
            FROM tickets t
            LEFT JOIN categories c
                ON t.category_id = c.category_id
            GROUP BY
                c.category_id,
                c.category_name
            ORDER BY total DESC
            """
        )

        category_stats = cursor.fetchall()

        # Priority statistics
        cursor.execute(
            """
            SELECT
                priority,
                COUNT(*) AS total
            FROM tickets
            GROUP BY priority
            ORDER BY total DESC
            """
        )

        priority_stats = cursor.fetchall()

        # Status statistics
        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) AS total
            FROM tickets
            GROUP BY status
            ORDER BY total DESC
            """
        )

        status_stats = cursor.fetchall()

        # Daily statistics
        cursor.execute(
            """
            SELECT
                DATE(created_at) AS ticket_date,
                COUNT(*) AS total
            FROM tickets
            GROUP BY DATE(created_at)
            ORDER BY ticket_date
            """
        )

        daily_stats = cursor.fetchall()

        return render_template(
            "analytics.html",
            category_stats=category_stats,
            priority_stats=priority_stats,
            status_stats=status_stats,
            daily_stats=daily_stats
        )

    finally:

        cursor.close()
        conn.close()


# ============================================================
# AI CHATBOT
# ============================================================

@app.route(
    "/chatbot",
    methods=["GET", "POST"]
)
@login_required
def chatbot():

    answer = None

    question = ""

    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        ).strip().lower()

        if (
            "ticket" in question
            and "create" in question
        ):

            answer = (
                "Go to Create Ticket and enter "
                "your subject and problem description."
            )

        elif "status" in question:

            answer = (
                "Open My Tickets to check "
                "the current ticket status."
            )

        elif "priority" in question:

            answer = (
                "The AI model predicts Low, Medium, "
                "High or Critical priority from ticket text."
            )

        elif "category" in question:

            answer = (
                "The AI model classifies tickets into "
                "Technical Issue, Account & Login, "
                "Payment, General Query or Feature Request."
            )

        elif "login" in question:

            answer = (
                "If you cannot login, check your "
                "username and password or register a new account."
            )

        else:

            answer = (
                "I can help with tickets, status, "
                "priority, category and login questions."
            )

    return render_template(
        "chatbot.html",
        answer=answer,
        question=question
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )