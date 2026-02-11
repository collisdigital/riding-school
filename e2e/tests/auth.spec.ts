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
  await expect(page.locator('text=No riders added yet.')).toBeVisible();
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
  await pageA.fill('input[placeholder="Rider First Name"]', 'Thunder');
  await pageA.fill('input[placeholder="Rider Last Name"]', 'Horse');
  await pageA.click('button:text("Add Rider")');
  await expect(pageA.locator('text=Thunder Horse')).toBeVisible();

  // Context B: Check that "Thunder Horse" is NOT visible
  await expect(pageB.locator('text=Thunder Horse')).not.toBeVisible();
  await expect(pageB.locator('text=No riders added yet.')).toBeVisible();

  // Context B: Add a rider "Lightning Flash"
  await pageB.fill('input[placeholder="Rider First Name"]', 'Lightning');
  await pageB.fill('input[placeholder="Rider Last Name"]', 'Flash');
  await pageB.click('button:text("Add Rider")');
  await expect(pageB.locator('text=Lightning Flash')).toBeVisible();

  // Context A: Check that "Lightning Flash" is NOT visible
  await expect(pageA.locator('text=Lightning Flash')).not.toBeVisible();
  await expect(pageA.locator('text=Thunder Horse')).toBeVisible();
});
