# encryptor.py — criptografia e descriptografia de payloads com Fernet

import base64
import hashlib
from cryptography.fernet import Fernet


def derivar_chave_fernet(token: str) -> Fernet:
    """
    Deriva uma chave Fernet a partir do token do agente.
    Usa SHA-256 para gerar 32 bytes e converte para base64 url-safe.
    Deve ser idêntico ao método usado na central.
    """
    chave = hashlib.sha256(token.encode()).digest()
    chave_b64 = base64.urlsafe_b64encode(chave)
    return Fernet(chave_b64)


def criptografar(conteudo: bytes, token: str) -> bytes:
    """Criptografa conteúdo usando chave derivada do token."""
    return derivar_chave_fernet(token).encrypt(conteudo)


def descriptografar(conteudo_enc: bytes, token: str) -> bytes:
    """Descriptografa conteúdo usando chave derivada do token."""
    return derivar_chave_fernet(token).decrypt(conteudo_enc)