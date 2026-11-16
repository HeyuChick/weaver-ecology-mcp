# -*- coding: utf-8 -*-
# Patch crypto.ts: pemToSingleLine + ensurePem helpers, wrap spk in rsaEncrypt.
import io

PATH = 'src/crypto.ts'

OLD_IMPORT = 'import forge from "node-forge";\r\nimport { Buffer } from "node:buffer";\r\n'

NEW_HELPERS = (
    'import forge from "node-forge";\r\n'
    'import { Buffer } from "node:buffer";\r\n'
    '\r\n'
    '/**\r\n'
    ' * PEM -> single-line base64 (Weaver cpk header format: no PEM armor, no newlines)\r\n'
    ' */\r\n'
    'export function pemToSingleLine(pem: string): string {\r\n'
    '  return pem\r\n'
    '    .replace(/-----BEGIN [^-]+-----/g, "")\r\n'
    '    .replace(/-----END [^-]+-----/g, "")\r\n'
    '    .replace(/\\s+/g, "");\r\n'
    '}\r\n'
    '\r\n'
    '/**\r\n'
    ' * Weaver returns spk as single-line base64; forge needs a full PEM.\r\n'
    ' * Wrap it with 64-char folding.\r\n'
    ' */\r\n'
    'export function ensurePem(singleLineKey: string): string {\r\n'
    '  if (singleLineKey.includes("BEGIN")) return singleLineKey;\r\n'
    '  const b64 = singleLineKey.replace(/\\s+/g, "");\r\n'
    '  const lines = b64.match(/.{1,64}/g) || [];\r\n'
    '  return "-----BEGIN PUBLIC KEY-----\\n" + lines.join("\\n") + "\\n-----END PUBLIC KEY-----";\r\n'
    '}\r\n'
)

OLD_ENC = 'export function rsaEncrypt(plainText: string, publicKeyPem: string): string {\r\n  const publicKey = forge.pki.publicKeyFromPem(publicKeyPem);'
NEW_ENC = 'export function rsaEncrypt(plainText: string, publicKeyPem: string): string {\r\n  const publicKey = forge.pki.publicKeyFromPem(ensurePem(publicKeyPem));'

with io.open(PATH, 'r', encoding='utf-8', newline='') as f:
    s = f.read()

assert s.count(OLD_IMPORT) == 1, 'import anchor: %d' % s.count(OLD_IMPORT)
assert s.count(OLD_ENC) == 1, 'rsaEncrypt anchor: %d' % s.count(OLD_ENC)

s = s.replace(OLD_IMPORT, NEW_HELPERS).replace(OLD_ENC, NEW_ENC)

with io.open(PATH, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('crypto.ts patched')
