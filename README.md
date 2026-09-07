# Hackathon Frontend (Draft — No Backend Yet)

This is a **frontend-only** draft. There is no server and no database.
Sign up / login / verify all just update local React state (in `AuthContext.jsx`)
so you can click through the whole flow and see the UI work end-to-end.

When the backend is ready, only `context/AuthContext.jsx` needs to change —
swap the mock functions for real `axios` calls to your API. Every page
(`SignUp`, `Login`, `Verify`, `Landing`) already calls `useAuth()`, so they
won't need to change.

## Run it
```bash
npm install
npm run dev
```
Opens at http://localhost:3000
