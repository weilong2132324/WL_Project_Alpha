VueJS:
Important Files:
(1) index.html --> Browswer Entry point. Placeholder is <div id="app"></div>
(2) src/main.js --> Logic Entry Point. First javascript file executed. Imports root component (App.vue) and mounts the application into the "app" div in index.html

(3) package.json --> List broadly the dependencies needed and versions broadly needed
(4) package_lock.json --> List dependencies actually needed.
(5) env --> Stores environment variables
(6) src --> contains the bulk of the application code
(6a) components --> reusable components 
(6b) views --> Full page components associated with URLs
(6c) router --> Configures URL routing 
(6d) store --> State Management

Go:
Important Files:
(1) go.mod (Dependencies)
(2) go.sum (Dependency checksums - like a package-lock.json)
(3) main.go (entry point)
(4) vendor/
(5) pkg
(5a) controllers --> Handles API routes, the usual crud operations
(5b) middleware/ --> Request interceptors 
(5c) model --> database schema

(6) Internal 
(6a) database --> DB connection + migrations
(6b) config --> Environment variables
(6c) service --> Business logic.
