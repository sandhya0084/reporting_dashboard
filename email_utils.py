def send_verification_email(app, user, mail):
    from flask_mail import Message
    from itsdangerous import URLSafeTimedSerializer
    from flask import url_for

    s = URLSafeTimedSerializer(app.secret_key)
    token = s.dumps(user.email, salt="email-confirm")

    # Build an absolute verification URL
    verify_url = url_for("verify_email", token=token, _external=True)

    # Determine sender and recipients safely
    sender = app.config.get("MAIL_USERNAME") or app.config.get("MAIL_DEFAULT_SENDER") or "noreply@example.com"
    recipients = [user.email]

    msg = Message(
        "Verify Your Email",
        sender=sender,
        recipients=recipients,
    )
    msg.body = f"Hi {user.username},\n\nClick this link to verify your account:\n{verify_url}"

    # If SMTP credentials are not configured, print (log) the verification URL
    mail_username = app.config.get("MAIL_USERNAME")
    mail_password = app.config.get("MAIL_PASSWORD")

    if not mail_username or not mail_password:
        # Dev fallback: print the verification URL so developers can copy it
        print("SMTP not configured. Development fallback: verification URL:", verify_url)
        return

    try:
        with app.app_context():
            mail.send(msg)
        print(f"Verification email sent to {user.email}")
    except Exception as e:
        # Log and re-raise so callers (routes) can present a helpful message
        print(f"Failed to send email to {user.email}: {str(e)}")
        raise
