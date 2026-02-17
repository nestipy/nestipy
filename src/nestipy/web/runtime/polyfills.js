(function () {
  if (typeof globalThis.process === "undefined") {
    globalThis.process = { env: { NODE_ENV: "production" } };
  } else {
    globalThis.process.env = globalThis.process.env || {};
    if (!("NODE_ENV" in globalThis.process.env)) {
      globalThis.process.env.NODE_ENV = "production";
    }
  }

  if (typeof globalThis.global === "undefined") {
    globalThis.global = globalThis;
  }

  if (typeof globalThis.queueMicrotask === "undefined") {
    globalThis.queueMicrotask = (cb) => Promise.resolve().then(cb);
  }

  if (globalThis.MessageChannel) return;

  class Port {
    constructor() {
      this.onmessage = null;
      this._other = null;
      this._closed = false;
    }

    postMessage(data) {
      if (this._closed) return;
      const other = this._other;
      if (!other || other._closed) return;

      globalThis.queueMicrotask(() => {
        if (other.onmessage) other.onmessage({ data });
      });
    }

    close() {
      this._closed = true;
      this.onmessage = null;
      this._other = null;
    }

    start() {}
  }

  globalThis.MessageChannel = class MessageChannel {
    constructor() {
      this.port1 = new Port();
      this.port2 = new Port();
      this.port1._other = this.port2;
      this.port2._other = this.port1;
    }
  };
})();
