import { test as base, type Page, type BrowserContext } from '@playwright/test';

/**
 * Attaches a console listener to the page that logs browser errors to the terminal.
 * This is useful for catching runtime errors during E2E tests.
 */
export const addConsoleListener = (page: Page) => {
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      console.log(`BROWSER ERROR: "${msg.text()}"`);
    }
  });
};

export const test = base.extend<{ context: BrowserContext }>({
  context: async ({ context }, use) => {
    // Listen for new pages in the default context and attach the listener
    context.on('page', (page) => {
      addConsoleListener(page);
    });
    await use(context);
  },
  // The default 'page' fixture is created via 'context.newPage()', so the above
  // context.on('page') listener will automatically attach to it.
  // We do not need to extend the 'page' fixture separately.
});

export { expect } from '@playwright/test';
