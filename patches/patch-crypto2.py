# -*- coding: utf-8 -*-
# Patch 2: rsaEncrypt uses PKCS1v15 (empirically verified against test E9 applytoken).
import io

PATH = 'src/crypto.ts'

OLD = (
    '/**\r\n'
    ' * 使用公钥加密 (RSA-OAEP / SHA-256)\r\n'
    ' * 泛微 E9 的 rsa.encrypt 默认使用 RSA/ECB/OAEPWITHSHA-256ANDMGF1PADDING\r\n'
    ' */\r\n'
    'export function rsaEncrypt(plainText: string, publicKeyPem: string): string {\r\n'
    '  const publicKey = forge.pki.publicKeyFromPem(ensurePem(publicKeyPem));\r\n'
    '  const encrypted = publicKey.encrypt(plainText, "RSA-OAEP", {\r\n'
    '    md: forge.md.sha256.create(),\r\n'
    '    mgf: forge.mgf.mgf1.create(forge.md.sha256.create()),\r\n'
    '  });\r\n'
    '  return forge.util.encode64(encrypted);\r\n'
    '}'
)

NEW = (
    '/**\r\n'
    ' * 使用公钥加密 (PKCS#1 v1.5)\r\n'
    ' * 实测泛微 E9 测试端 applytoken/userid 解密使用 RSAES-PKCS1-V1_5（OAEP 全系被拒）。\r\n'
    ' * 2026-11 对真实 E9 测试环境逐项实测：OAEP-SHA256/SOAEP-SHA1 均返回 secret解密失败。\r\n'
    ' */\r\n'
    'export function rsaEncrypt(plainText: string, publicKeyPem: string): string {\r\n'
    '  const publicKey = forge.pki.publicKeyFromPem(ensurePem(publicKeyPem));\r\n'
    '  const encrypted = publicKey.encrypt(plainText, "RSAES-PKCS1-V1_5");\r\n'
    '  return forge.util.encode64(encrypted);\r\n'
    '}'
)

with io.open(PATH, 'r', encoding='utf-8', newline='') as f:
    s = f.read()
assert s.count(OLD) == 1, 'anchor: %d' % s.count(OLD)
s = s.replace(OLD, NEW)
with io.open(PATH, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('crypto.ts rsaEncrypt -> PKCS1v15')
