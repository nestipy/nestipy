import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

// https://vitepress.dev/reference/site-config
export default withMermaid(defineConfig({
  title: "Nestipy",
  description: "A Python framework inspired by NestJS and built on top of FastAPI or Blacksheep.",
  srcDir: '.',
  outDir: '../docs', 
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    logo: '/images/nestipy.png',
    
    nav: [],

    sidebar: [
      {
        text: 'Overview',
        items: [
          { text: 'First steps', link: '/overview/first-step' },
          { text: 'Controllers', link: '/overview/controller' },
          { text: 'Providers', link: '/overview/provider' },
          { text: 'Modules', link: '/overview/module' },
          { text: 'Middlewares', link: '/overview/middleware' },
          { text: 'Exceptions filters', link: '/overview/exception-filter' },
          { text: 'Guards', link: '/overview/guard' },
          { text: 'Interceptors', link: '/overview/interceptor' },
          { text: 'Pipes', link: '/overview/pipes' },
          { text: 'Scopes + Pipes + Lifecycle', link: '/overview/scopes-pipes-lifecycle' },
          { text: 'Devtools Graph', link: '/overview/devtools' },
          { text: 'Typed Client', link: '/overview/typed-client' },
          { text: 'Custom decorators', link: '/overview/custom-decorator' },
        ]
      },
      {
        text: 'Fundamentals',
        items: [
          { text: 'Custom providers', link: '/fundamental/custom-provider' },
          { text: 'Dynamic modules', link: '/fundamental/dynamic-module' },
          { text: 'Execution context', link: '/fundamental/execution-context' },
          { text: 'Lifecycle events', link: '/fundamental/lifecycle-event' },
          { text: 'DI and Request Scope', link: '/fundamental/di-request-scope' },
          { text: 'Build a module', link: '/fundamental/build-module' },
          { text: 'Testing', link: '/fundamental/testing' },
        ]
      },
      {
        text: 'Techniques',
        items: [
          { text: 'Configuration', link: '/technique/configuration' },
          { text: 'Database', link: '/technique/database' },
          { text: 'Task scheduling', link: '/technique/schedule' },
          { text: 'Background Tasks', link: '/technique/background_task' },
          { text: 'Events', link: '/technique/event' },
          { text: 'Inertia', link: '/technique/inertia' },
          { text: 'Benchmark', link: '/technique/benchmark' },
        ]
      },
      {
        text: 'GraphQL',
        items: [
          { text: 'Quick start', link: '/graphql/quick-start' },
          { text: 'Resolvers', link: '/graphql/resolver' },
          { text: 'Mutations', link: '/graphql/mutation' },
          { text: 'Subscription', link: '/graphql/subscription' },
        ]
      },
      {
        text: 'Websockets',
        items: [
          { text: 'Gateways', link: '/websocket/gateway' },
          { text: 'Adapters', link: '/websocket/adapter' },
        ]
      },
      {
        text: 'Microservices',
        items: [
          { text: 'Overview', link: '/microservice/overview' },
          { text: 'Redis', link: '/microservice/redis' },
          { text: 'MQTT', link: '/microservice/mqtt' },
          { text: 'NATS', link: '/microservice/nats' },
          { text: 'RabbitMQ', link: '/microservice/rabbitmq' },
          { text: 'GRPC', link: '/microservice/grpc' },
        ]
      },
      {
        text: 'Web',
        items: [
          { text: 'Overview', link: '/web/' },
          { text: 'Getting Started', link: '/web/getting-started' },
          { text: 'Routing + Layouts', link: '/web/routing-layouts' },
          { text: 'Components + UI', link: '/web/components' },
          { text: 'Actions (RPC)', link: '/web/actions' },
          { text: 'Typed Clients', link: '/web/typed-clients' },
          { text: 'CLI', link: '/web/cli' },
          { text: 'Environment', link: '/web/environment' },
          { text: 'Production', link: '/web/production' },
          { text: 'SSR', link: '/web/ssr' },
          { text: 'Troubleshooting', link: '/web/troubleshooting' },
        ]
      },
      { text: 'OpenAPI', link: '/openapi/start' },
      {
        text: 'Recipes',
        items: [
          { text: 'REPL', link: '/recipes/repl' },
          { text: 'Router module', link: '/recipes/router' },
          { text: 'Commander', link: '/recipes/commander' },
          { text: 'Auth + Guards + Pipes + OpenAPI', link: '/recipes/auth-guards-pipes-openapi' },
        ]
      },
      { text: 'CLI', link: '/cli' },
      { text: 'Utils', link: '/util' },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/nestipy/nestipy' },
      { icon: 'x', link: 'https://x.com/nestipy' },
      { icon: 'linkedin', link: 'https://linkedin.com/in/nestipy' }
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024 Nestipy'
    },

    search: {
      provider: 'local'
    }
  },
  markdown: {
    theme: {
      light: 'github-light',
      dark: 'dracula'
    },
    lineNumbers: true
  },
  mermaid: {},
}))
