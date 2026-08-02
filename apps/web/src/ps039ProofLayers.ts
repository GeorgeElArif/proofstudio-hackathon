export type ProofLayerAccent = "cyan" | "archive-orange";

export type ProofLayer = {
  id: string;
  label: string;
  descriptor: string;
  body: string;
  accent: ProofLayerAccent;
  evidencePreview: string;
  mustNotClaim: string[];
};

export const PS039_TRUTH_BOUNDARY =
  "Proof is not truth.\nProof is the record.";

export const PS039_PROOF_LAYERS: ProofLayer[] = [
  {
    id: "prompt",
    label: "PROMPT",
    descriptor: "What started the run.",
    body: "What started the run.",
    accent: "cyan",
    evidencePreview: "Request context.",
    mustNotClaim: ["semantic truth", "human-made media"],
  },
  {
    id: "provider-model",
    label: "PROVIDER · MODEL",
    descriptor: "The model context attached.",
    body: "The model context attached.",
    accent: "cyan",
    evidencePreview: "Model context.",
    mustNotClaim: ["provider availability", "model output truth"],
  },
  {
    id: "b2-archive",
    label: "B2 ARCHIVE",
    descriptor: "Where the accepted record points.",
    body: "Where the accepted record points.",
    accent: "archive-orange",
    evidencePreview: "Archive reference.",
    mustNotClaim: ["browser byte verification", "storage immutability"],
  },
  {
    id: "genblaze-manifest",
    label: "GENBLAZE MANIFEST",
    descriptor: "What the run captured.",
    body: "What the run captured.",
    accent: "cyan",
    evidencePreview: "Manifest context.",
    mustNotClaim: ["semantic truth", "legal authenticity"],
  },
  {
    id: "rehydrate-check",
    label: "REHYDRATE CHECK",
    descriptor: "The retrieval check outcome.",
    body: "The retrieval check outcome.",
    accent: "cyan",
    evidencePreview: "Check outcome.",
    mustNotClaim: ["browser byte verification", "storage availability"],
  },
  {
    id: "review-decision",
    label: "REVIEW DECISION",
    descriptor: "What the reviewer decided.",
    body: "What the reviewer decided.",
    accent: "cyan",
    evidencePreview: "Workflow decision.",
    mustNotClaim: ["legal clearance", "authenticity"],
  },
  {
    id: "provenance-passport",
    label: "PROVENANCE PASSPORT",
    descriptor: "The record that travels.",
    body: "The record that travels.",
    accent: "cyan",
    evidencePreview: "Inspection record.",
    mustNotClaim: ["semantic truth", "human-made media"],
  },
  {
    id: "export-pack",
    label: "EXPORT PACK",
    descriptor: "What leaves the room.",
    body: "The portable export pack.",
    accent: "cyan",
    evidencePreview: "Export pack.",
    mustNotClaim: ["campaign performance", "deployment guarantee"],
  },
];

export const PS039_STORY_STATES = [
  "sealed",
  "stabilizing",
  "split",
  "boundary",
  "room",
] as const;

export type Ps039StoryState = (typeof PS039_STORY_STATES)[number];
