import { test, expect } from '@playwright/test';

test('full user journey: register -> create school -> dashboard', async ({ page }) => {
  const email = `owner-${Math.random().toString(36).substring(7)}@example.com`;
  
  // 1. Landing Page
  await page.goto('/');
  await expect(page.locator('text=Track Rider Progress with Precision.')).toBeVisible();
  await page.click('text=Register Your School');

  // 2. Registration
  await expect(page).toHaveURL('/register');
  await page.fill('input[type="text"]:near(:text("First Name"))', 'John');
  await page.fill('input[type="text"]:near(:text("Last Name"))', 'Doe');
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', 'Password123!');
  await page.click('button:text("Create Account")');

  // 3. Onboarding: Create School
  await expect(page).toHaveURL('/onboarding/create-school', { timeout: 10000 });
  await page.fill('input[placeholder="e.g. Willow Creek Equestrian"]', 'Willow Creek');
  await page.click('button:text("Create School & Start Tracking")');

  // 4. Dashboard
  await expect(page).toHaveURL('/dashboard', { timeout: 10000 });
  await expect(page.locator('text=Willow Creek')).toBeVisible();
  // The dashboard overview now shows stats, not "No riders added yet" (that's on the Riders page)
  // We can verify "Total Riders" text instead
  await expect(page.locator('text=Total Riders')).toBeVisible();
});

test('multi-tenant leak test', async ({ browser }) => {
  const emailA = `owner-a-${Math.random().toString(36).substring(7)}@example.com`;
  const emailB = `owner-b-${Math.random().toString(36).substring(7)}@example.com`;

  // Context A: Create School A and a Rider
  const contextA = await browser.newContext();
  const pageA = await contextA.newPage();
  
  await pageA.goto('/register');
  await pageA.fill('input[type="text"]:near(:text("First Name"))', 'Alice');
  await pageA.fill('input[type="text"]:near(:text("Last Name"))', 'Owner');
  await pageA.fill('input[type="email"]', emailA);
  await pageA.fill('input[type="password"]', 'Password123!');
  await pageA.click('button:text("Create Account")');
  
  await pageA.waitForURL('/onboarding/create-school');
  await pageA.fill('input[placeholder="e.g. Willow Creek Equestrian"]', 'School A');
  await pageA.click('button:text("Create School & Start Tracking")');
  await pageA.waitForURL('/dashboard');

  // Context B: Create School B
  const contextB = await browser.newContext();
  const pageB = await contextB.newPage();
  
  await pageB.goto('/register');
  await pageB.fill('input[type="text"]:near(:text("First Name"))', 'Bob');
  await pageB.fill('input[type="text"]:near(:text("Last Name"))', 'Owner');
  await pageB.fill('input[type="email"]', emailB);
  await pageB.fill('input[type="password"]', 'Password123!');
  await pageB.click('button:text("Create Account")');
  
  await pageB.waitForURL('/onboarding/create-school');
  await pageB.fill('input[placeholder="e.g. Willow Creek Equestrian"]', 'School B');
  await pageB.click('button:text("Create School & Start Tracking")');
  await pageB.waitForURL('/dashboard');

  // Context A: Add a rider "Thunder Horse"
  // NOTE: Upstream changed navigation to 'Riders' page.
  // BUT my changes in DashboardPage.tsx KEPT the form on the main dashboard for now (to preserve my work).
  // So I should stick to my selectors, but maybe upstream navigation isn't needed if the form is on Dashboard.
  // HOWEVER, upstream `DashboardPage` seemed to remove the form?
  // Wait, in `Resolve Conflicts in frontend/src/pages/DashboardPage.tsx`, I KEPT the form.
  // So I don't need to navigate to 'Riders'.

  await pageA.fill('input#rider-first-name', 'Thunder');
  await pageA.fill('input#rider-last-name', 'Horse');
  await pageA.click('button:text("Add Rider")');
  await expect(pageA.locator('text=Thunder Horse')).toBeVisible();

  // Context B: Check that "Thunder Horse" is NOT visible
  // If the list is also on Dashboard (which I kept), I can check there.
  await expect(pageB.locator('text=Thunder Horse')).not.toBeVisible();
  // Upstream changed "No riders added yet" to "No riders found matching your search" on Riders page.
  // My DashboardPage still has "No riders added yet".
  await expect(pageB.locator('text=No riders added yet.')).toBeVisible();

  // Context B: Add a rider "Lightning Flash"
  await pageB.fill('input#rider-first-name', 'Lightning');
  await pageB.fill('input#rider-last-name', 'Flash');
  await pageB.click('button:text("Add Rider")');
  await expect(pageB.locator('text=Lightning Flash')).toBeVisible();

  // Context A: Check that "Lightning Flash" is NOT visible
  await expect(pageA.locator('text=Lightning Flash')).not.toBeVisible();
  await expect(pageA.locator('text=Thunder Horse')).toBeVisible();
});
