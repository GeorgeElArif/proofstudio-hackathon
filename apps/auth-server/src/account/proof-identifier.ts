export const PROOF_IDENTIFIER_MAX_LENGTH = 128;
export const PROOF_IDENTIFIER_GRAMMAR = /^[A-Za-z0-9_.:-]{1,128}$/;

export function isValidProofIdentifier(value: unknown): value is string {
  return typeof value === "string" &&
    value === value.normalize("NFC") &&
    PROOF_IDENTIFIER_GRAMMAR.test(value);
}

export function encodeProofIdentifier(value: string): string {
  if (!isValidProofIdentifier(value)) throw new Error("invalid_proof_identifier");
  return encodeURIComponent(value);
}
