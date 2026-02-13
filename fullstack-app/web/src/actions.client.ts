import { createActionClient, ActionResponse, ActionClientOptions, createActionMetaProvider } from './actions';

export function createActions(options: ActionClientOptions = {}) {
  const call = createActionClient({ ...options, endpoint: options.endpoint ?? '/_actions', meta: options.meta ?? createActionMetaProvider() });
  return {
    AppActions: {
      hello: (params: { name?: string }) => call<string>("AppActions.hello", [], params as Record<string, unknown>),
    },
    call,
  };
}
