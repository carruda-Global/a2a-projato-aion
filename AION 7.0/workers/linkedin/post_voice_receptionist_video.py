"""One-off: publish the AION Voice Receptionist cover video with a consulting
pitch, using the real LinkedIn agent (LinkedInIntegration), not the browser."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from integrations import LinkedInIntegration, LinkedInConfig

VIDEO_PATH = r"C:\Users\crist\Downloads\AION_Voice_Receptionist_Cover.mp4"

TEXT = """\U0001F680 Apresento o AION Voice Receptionist -- um recepcionista de IA que atende ligacoes 24/7 para pequenas empresas, nunca perde uma chamada, e ainda manda mensagem de volta com link de agendamento para quem nao conseguiu ser atendido na hora.

Construido com tecnologia de producao real: LangGraph, DeepSeek, Vapi.ai, e base de conhecimento propria por cliente -- nao e prototipo, e um produto ativo com cliente pagante de verdade.

Se voce (ou sua empresa) precisa de um agente de IA assim, ou de qualquer solucao sob medida em Inteligencia Artificial -- estamos a disposicao para prestacao de servico de consultoria. Comenta aqui ou manda mensagem."""


async def main():
    linkedin = LinkedInIntegration(config=LinkedInConfig())
    await linkedin.initialize()
    try:
        video_bytes = Path(VIDEO_PATH).read_bytes()
        print(f"Uploading video ({len(video_bytes)} bytes)...")
        upload = await linkedin.tools.upload_video(video_bytes, "AION_Voice_Receptionist_Cover.mp4")
        if "error" in upload:
            print("UPLOAD FAILED:", upload)
            return
        print("Video uploaded, asset:", upload["asset"])

        result = await linkedin.tools.create_post_with_video(
            text=TEXT, video_asset=upload["asset"], title="AION Voice Receptionist"
        )
        print("POST RESULT:", result)
    finally:
        await linkedin.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
