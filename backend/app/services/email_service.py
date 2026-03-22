import logging
import resend
from app.core.config import settings

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


class EmailService:
    @staticmethod
    async def send_magic_link(email: str, company_name: str, token: str) -> bool:
        """Send magic link email via Resend."""
        survey_url = f"{settings.FRONTEND_URL}/survey?token={token}"
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">Convite para Pesquisa de Clima Organizacional</h2>
            <p>Prezado(a) colaborador(a),</p>
            <p>Você foi convidado(a) para participar da <strong>Pesquisa de Risco Psicossocial</strong>
            de <strong>{company_name}</strong>, em conformidade com a NR-1.</p>
            <p>Sua participação é fundamental para garantir um ambiente de trabalho mais saudável e seguro.</p>
            <p><strong>Importante:</strong></p>
            <ul>
                <li>A pesquisa é completamente anônima</li>
                <li>Suas respostas são protegidas pela LGPD</li>
                <li>O link é válido por 24 horas</li>
                <li>Pode ser respondida apenas uma vez</li>
            </ul>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{survey_url}"
                   style="background-color: #2563eb; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; font-size: 16px;">
                    Responder Pesquisa
                </a>
            </p>
            <p style="color: #666; font-size: 12px;">
                Se você não conseguir clicar no botão, copie e cole o link abaixo no seu navegador:<br>
                <a href="{survey_url}">{survey_url}</a>
            </p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 11px;">
                Este email foi enviado automaticamente. Não responda a este email.
            </p>
        </body>
        </html>
        """
        try:
            params = {
                "from": "VIVA Psicossocial <noreply@viva.app>",
                "to": [email],
                "subject": f"Convite para Pesquisa de Clima - {company_name}",
                "html": html_body,
            }
            response = resend.Emails.send(params)
            logger.info(f"Magic link sent to {email}, resend id: {response.get('id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to send magic link email: {e}")
            return False
