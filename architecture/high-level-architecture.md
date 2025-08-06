# High Level Architecture

## Technical Summary
This architecture describes a modern, serverless web application using a Jamstack approach. The frontend is a **Next.js** application hosted on **Vercel**. The backend is powered by **Supabase**, which handles the database, user authentication, and serverless functions. This design prioritizes performance, scalability, and development speed.

## Platform and Infrastructure Choice
* **Platform:** **Vercel** for the frontend and **Supabase** for the backend.
* **Key Services:** Vercel (CDN, CI/CD), Supabase (Auth, PostgreSQL Database, Storage, Edge Functions).

## Repository Structure
* **Structure:** **Monorepo**.
* **Monorepo Tool:** **Turborepo**.

## High Level Architecture Diagram
```mermaid
graph TD
    User -->|Browser| A[Next.js Frontend on Vercel]
    A -->|API Calls / Auth| B[Supabase BaaS]
    B --> C[User Authentication]
    B --> D[PostgreSQL Database]