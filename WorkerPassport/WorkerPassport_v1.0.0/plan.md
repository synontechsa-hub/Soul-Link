# WorkerPassport – Project Plan

**Self-Sovereign Career & Safety Passport on Blockchain**  
*Portable, verifiable credentials for work history, skills, and health & safety certifications*

Current date: March 2026  
Author: Synonimity (@Adam8403)  
Version: 0.1 – MVP Planning Stage

## 1. Vision & Core Problem Solved

**One-liner:**  
A mobile-first, blockchain-powered digital passport that lets workers own, carry, and instantly prove their employment history, skills, and safety certifications — forever, across jobs, borders, and platforms — without middlemen or fraud.

**Key problems addressed (2026 reality):**

- Credential fraud & fake certificates (especially safety training)
- Slow, expensive background & reference checks for employers
- Lost paperwork when changing jobs, countries, or gig platforms
- Duplicated retraining for migrant/gig workers
- Lack of portable safety records in high-risk industries (construction, mining, logistics, manufacturing)
- Regulatory push for electronic, verifiable records (EU eIDAS 2.0, OSHA electronic tracking, etc.)

**Target users – Phase 1 focus:**

- Blue-collar & gig workers (construction, mining, delivery, security in SA/Africa)
- Training providers (NOSA, Red Cross equivalents, private safety trainers)
- Small-to-medium employers & subcontractors who need fast verification

## 2. Core Value Propositions

For **Workers** (free tier):

- Own your credentials forever in your wallet
- Selective disclosure (prove “valid forklift cert” without showing full history)
- Expiry alerts & renewal reminders
- Instant sharing via QR or link

For **Employers/HR** (paid):

- Instant, cryptographic verification (seconds, not weeks)
- Reduce fraud risk & hiring delays
- Bulk verification API for ATS integration

For **Issuers** (training providers/previous employers):

- Easy issuance of tamper-proof VCs
- New revenue from verification micro-fees

## 3. MVP Scope (Phase 1 – 8–12 weeks target)

### Must-have features

1. Worker mobile app
   - Wallet creation (simple onboarding: email/social + passkey or seed phrase backup)
   - Dashboard: list of held credentials + expiry dates
   - Add credential: manual upload + basic OCR scan (paper certs)
   - Share credential: generate QR/link with selective disclosure

2. Credential types supported (start small)
   - Safety training certs (e.g. OSHA 10/30 equivalent, Working at Heights, First Aid)
   - Employment confirmation letter (basic VC from previous employer)
   - Forklift / heavy machinery ticket
   - Expiry date + revocation status

3. Issuer web dashboard (minimal)
   - Login → issue VC to worker (by email or wallet address)
   - Pre-filled templates for common certs

4. Verifier flow
   - Scan QR or paste link → show validity/expiry/revocation
   - Basic web page or mobile deep-link for verifiers

5. Blockchain backend
   - Store VC hashes + revocation registry
   - Use IPFS for full documents (optional encryption)

### Out of MVP (Phase 2+)

- Full employment history timeline
- Gig contract escrow / milestone payments
- Bulk import from legacy systems
- Advanced analytics for employers
- Cross-chain support
- Full EU eIDAS Wallet compatibility

## 4. Tech Stack (Python-friendly where possible)

- **Frontend**  
  Flutter (mobile + web) – cross-platform, beautiful UI, good for QR/camera

- **Backend**  
  Python + FastAPI (REST API, auth, business logic)  
  Optional: Celery + Redis for background tasks (e.g. notifications)

- **Blockchain**  
  Chain: Polygon (cheap, mature ecosystem) or Base (Coinbase-backed, growing fast)  
  Smart contracts: Solidity (use OpenZeppelin templates)  
  Framework: Brownie or Hardhat (Brownie is Pythonic – aligns with your comfort)  
  VC library: Veramo (JS/TS) or SpruceID/KILT SDK – abstract DID/VC creation & verification  
  Wallet integration: WalletConnect v2 + embedded option (Privy or Dynamic for easy onboarding)

- **Storage**  
  IPFS (via Pinata or Infura) for documents  
  Only hash + metadata on-chain

- **Auth & Identity**  
  DID (Decentralized Identifiers) via Veramo  
  Simple email/social login → link to wallet (no forced crypto UX day 1)

- **DevOps**  
  Docker + Docker Compose for local dev  
  Vercel/Netlify for issuer/verifier web  
  Railway/Fly.io for FastAPI backend

## 5. Milestones & Timeline (Rough – 8–12 weeks MVP)

Week 1–2  

- Finalize name, logo sketch, folder structure  
- Set up repo + monorepo (or separate frontend/backend)  
- Research & decide exact chain + VC library  
- Write basic Solidity revocation registry contract

Week 3–4  

- Flutter skeleton: wallet connect, dashboard screen  
- FastAPI backend: user auth, credential metadata endpoints  
- Deploy testnet smart contracts

Week 5–6  

- Implement VC issuance (issuer dashboard)  
- OCR scan → hash → IPFS upload flow  
- QR generation + verification endpoint

Week 7–8  

- End-to-end test: issue → hold → share → verify  
- Polish UI/UX (onboarding, error messages)  
- Basic tests (unit + integration)

Week 9–10  

- Security basics: input validation, rate limiting  
- Deploy to testnet + internal testing  
- Gather feedback from 5–10 construction workers/trainers

Week 11–12 (if needed)  

- Bug fixes, performance tweaks  
- Prepare pitch deck / one-pager for potential partners  
- Launch private beta (Johannesburg focus)

## 6. Risks & Mitigations

- Crypto UX too hard → Use Privy/Dynamic for invisible wallets first  
- Regulatory uncertainty → Start with non-financial VCs (certs only), align with W3C standards  
- Adoption chicken-egg → Seed with local training providers (offer free issuance)  
- Cost of on-chain ops → Polygon/Base cheap; batch revocations if needed

## 7. Early Success Metrics

- 50 workers create wallets & add ≥1 credential  
- 5 training providers issue test certs  
- 10 successful verifications by real employers  
- No major security incidents in beta

## 8. Folder Structure Suggestion

WorkerPassport/
├── plan.md                 ← you are here
├── README.md
├── backend/                # FastAPI + Python
│   ├── app/
│   ├── contracts/          # Brownie project
│   └── tests/
├── frontend/               # Flutter app
│   ├── lib/
│   └── test/
├── docs/                   # architecture diagrams, flows
├── .env.example
└── docker-compose.yml
