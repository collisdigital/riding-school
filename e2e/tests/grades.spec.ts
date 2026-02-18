import { test, expect } from '@playwright/test';

test('grades curriculum builder', async ({ page }) => {
  const email = `owner-grades-${Math.random().toString(36).substring(7)}@example.com`;

  // 1. Register and Create School
  await page.goto('/register');
  // Use ID selectors for reliability
  await page.fill('#firstName', 'Curriculum');
  await page.fill('#lastName', 'Builder');
  await page.fill('#email', email);
  await page.fill('#password', 'Password123!');
  await page.click('button:text("Create Account")');

  await page.waitForURL('/onboarding/create-school');
  await page.fill('input[placeholder="e.g. Willow Creek Equestrian"]', 'Grades School');
  await page.click('button:text("Create School & Start Tracking")');
  await page.waitForURL('/dashboard');

  // 2. Navigate to Grades
  await page.click('text=Grades');
  await expect(page).toHaveURL('/dashboard/grades');

  // 3. Add Grade "Level 1"
  await page.click('button:text("Add Grade")');
  await page.fill('input[placeholder="e.g. Grade 1 - Beginner"]', 'Level 1');
  await page.fill('textarea[placeholder="Brief description of requirements..."]', 'Beginner level');
  await page.click('button:text("Create Grade")');

  await expect(page.locator('h3:text("Level 1")')).toBeVisible();

  // 4. Add Grade "Level 2"
  await page.click('button:text("Add Grade")');
  await page.fill('input[placeholder="e.g. Grade 1 - Beginner"]', 'Level 2');
  await page.click('button:text("Create Grade")');

  await expect(page.locator('h3:text("Level 2")')).toBeVisible();

  // 5. Select Level 1 and Add Skill
  await page.click('h3:text("Level 1")'); // Select
  await expect(page.locator('h2:text("Level 1")')).toBeVisible(); // Header in SkillList

  await page.click('button:text("Add Skill")');
  await page.fill('input[placeholder="e.g. Rising Trot"]', 'Walk');
  await page.click('button:text("Add Skill")'); // Submit

  await expect(page.locator('h3:text("Walk")')).toBeVisible();

  // 6. Delete Level 2
  page.on('dialog', dialog => dialog.accept());

  // Find the delete button for Level 2
  const level2Item = page.locator('div').filter({ has: page.locator('h3:text("Level 2")') }).first();
  await level2Item.locator('button[aria-label="Delete grade"]').click();

  await expect(page.locator('h3:text("Level 2")')).not.toBeVisible();
  await expect(page.locator('h3:text("Level 1")')).toBeVisible();
});
