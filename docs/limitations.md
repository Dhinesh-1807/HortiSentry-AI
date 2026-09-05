# HortiSentry — System Limitations & Scope Boundaries

## Current System Limitations (Phase 2 Baseline)
1. **Decision Support Prototype:** HortiSentry is an AI-assisted observation system for academic evaluation; it is not a certified agricultural diagnostic system.
2. **Initial Single Active Crop Target:** The Phase 2 MVP targets Tomato (*Solanum lycopersicum*). Additional crops (Chilli, Brinjal, Potato) are configured in dynamic YAML schema as placeholders for future phases.
3. **ML Mode State:** Currently operating in **DEMO MODE** pending full dataset training in Phase 7. Predictions are deterministic mock values tagged with `"is_demo_mode": true`.
4. **Network Requirement:** Full real-time synchronization requires an active internet connection to communicate with the FastAPI backend. Offline queueing is identified in Future Scope.
