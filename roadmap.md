# Nestipy Evolution Roadmap: Optimizations and Refactoring

This document outlines the planned improvements for the Nestipy framework to enhance performance, flexibility, and testability.

## 1. Performance Optimization
To ensure that Nestipy's abstraction layer does not significantly degrade performance compared to the underlying frameworks:

- **ContextVar for Request Scope**: Replace the shared `_instance` in `RequestContextContainer` with `ContextVar` to ensure that concurrent requests do not overwrite each other's execution context. This is critical for high-concurrency async environments.
- **Handler Caching**: Implement caching for resolved route handlers and dependency injection graphs. Avoid re-calculating metadata on every request.
- **Minimal Context Creation**: Refactor `ExecutionContext` to be lazily evaluated. Some metadata or request properties might not be needed for every route.
- **Fast Reflect**: Optimize the `Reflect` utility, possibly by using a more efficient storage mechanism than standard dictionary updates on the object itself.
- **Overhead Reduction in Proxy**: Streamline `RouterProxy` to reduce the number of `await` calls for basic requests that don't use guards or interceptors.

## 2. Generic and Pluggable Architecture
Facilitate the injection and replacement of core components:

- **Standardized Singleton Registry**: Refactor `NestipyContainer`, `MiddlewareContainer`, and other "application-level" singletons to use a unified registry to avoid redundant boilerplate and ensure consistent lifecycle management.
- **Unified Adapter Interface**: Standardize the interface for `HttpAdapter`, `WebsocketAdapter`, and `MicroserviceServer` to share common logic for metadata extraction and execution context management.
- **Pluggable DI Container**: Allow users to replace or extend the default `NestipyContainer` with other DI libraries if desired.
- **Dynamic Adapter Selection**: Improve the factory logic to allow switching adapters (e.g., from FastAPI to BlackSheep) with minimal configuration changes.

## 3. Code Understandability and API Design
Make the codebase more approachable for contributors:

- **Strict Typing**: Enforce strict typing across the entire codebase to improve IDE support and reduce runtime errors.
- **Modular Directory Structure**: Further separate core logic from framework-specific implementations (e.g., move OpenAPI logic out of the core router proxy).
- **Clear Exception Hierarchy**: Refactor exception types to be more descriptive and easier to catch at different levels of the application.

## 4. Testability and Coverage
Improve the reliability of the framework:

- **Decoupled Logic for Unit Testing**: Refactor classes like `NestipyContainer` and `RouterProxy` to depend on interfaces rather than concrete implementations, allowing for easier mocking.
- **Comprehensive Integration Tests**: Create a suite of tests that run against all supported adapters (FastAPI, BlackSheep) to ensure consistent behavior.
- **Targeting 100% Coverage**: Focus on covering the IOC container and the Proxy logic, which are the most critical and complex parts of the framework.
- **Test Utilities**: Provide a robust `TestingModule` and `Test` utility similar to NestJS to help users test their own applications built with Nestipy.
