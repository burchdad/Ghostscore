---
title: "Protect profile endpoints with authentication"
labels: [backend, security]
milestone: Authentication & Users
---

Ensure all profile modification endpoints are protected and only accessible by the profile owner.

- Add dependency injection for current user
- Return `403` when user is not owner
- Add unit + integration tests
