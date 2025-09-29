def send_verification_email(app, user, mail):
    from flask_mail import Message
    from itsdangerous import URLSafeTimedSerializer
    from flask import url_for

    s = URLSafeTimedSerializer(app.secret_key)
    token = s.dumps(user.email, salt="email-confirm")

    verify_url = url_for("verify_email", token=token, _external=True)

    msg = Message(
        "Verify Your Email",
        sender=app.config["MAIL_USERNAME"],
        recipients=[sandhyachirumamilla6@gmail.com],
    )
    msg.body = f"Hi {user.username},\n\nClick this link to verify your account:\n{verify_url}"

    try:
        with app.app_context():
            mail.send(msg)
        print(f" Verification email sent to {user.email}")
    except Exception as e:
        print(f" Failed to send email to {user.email}: {str(e)}")
