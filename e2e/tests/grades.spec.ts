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

  await expect(page).toHaveURL('/onboarding/create-school', { timeout: 15000 });
  await page.fill('input[placeholder="e.g. Willow Creek Equestrian"]', 'Curriculum Academy');
  await page.click('button:text("Create School & Start Tracking")');
  await expect(page).toHaveURL('/dashboard', { timeout: 15000 });

  // 2. Navigate to Grades
  // Target the sidebar specifically to avoid ambiguity
  await page.locator('nav').getByText('Grades').click();
  await expect(page).toHaveURL('/dashboard/grades');

  // Wait for network idle to ensure data is fetched
  await page.waitForLoadState('networkidle');

  // 3. Add Grade "Level 1"
  const addGradeBtn = page.locator('button', { hasText: 'Add Grade' });
  await expect(addGradeBtn).toBeVisible({ timeout: 15000 });
  await addGradeBtn.click();

  await page.fill('input[placeholder="e.g. Grade 1 - Beginner"]', 'Level 1');
  await page.fill('textarea[placeholder="Brief description of requirements..."]', 'Beginner level');
  await page.click('button:text("Create Grade")');

  await expect(page.locator('h3:text("Level 1")')).toBeVisible();

  // 4. Add Grade "Level 2"
  await addGradeBtn.click();
  await page.fill('input[placeholder="e.g. Grade 1 - Beginner"]', 'Level 2');
  await page.click('button:text("Create Grade")');

  await expect(page.locator('h3:text("Level 2")')).toBeVisible();

  // 5. Select Level 1 and Add Skill
  await page.click('h3:text("Level 1")'); // Select
  await expect(page.locator('h2:text("Level 1")')).toBeVisible(); // Header in SkillList

  const addSkillBtn = page.locator('button', { hasText: 'Add Skill' }).first();
  await expect(addSkillBtn).toBeVisible({ timeout: 15000 });
  await addSkillBtn.click();

  await page.fill('input[placeholder="e.g. Rising Trot"]', 'Walk');
  // Use specific submit button for skill modal to avoid confusion
  await page.locator('form').getByRole('button', { name: 'Add Skill' }).click();

  // Verify Skill added and count updated
  await expect(page.locator('h3:text("Walk")')).toBeVisible();
  // Check "1 skill" text in the grade list item (target specific div structure if needed, or just text)
  // Use .last() to find the Grade Item in the sidebar (most specific) or target by class if possible
  // GradeList item: flex items-center p-3 mb-2 bg-white rounded-lg border...
  // We can target the sidebar container explicitly.
  const gradeItem = page.locator('div').filter({ hasText: 'Level 1' }).filter({ hasText: '1 skill' });
  await expect(gradeItem.first()).toBeVisible();

  // 6. Edit Skill
  // Target the skill row specifically using the group class we added
  const skillRow = page.locator('.group').filter({ has: page.locator('h3:text("Walk")') }).first();
  await skillRow.hover();
  await skillRow.getByLabel('Edit skill').click();

  await expect(page.getByText('Edit Skill')).toBeVisible();
  await page.fill('input[value="Walk"]', 'Walk (Modified)');
  await page.locator('form').getByRole('button', { name: 'Save Changes' }).click();

  await expect(page.locator('h3:text("Walk (Modified)")')).toBeVisible();

  // 7. Delete Skill
  page.on('dialog', dialog => dialog.accept());
  // Re-acquire row as text changed
  const skillRowMod = page.locator('.group').filter({ has: page.locator('h3:text("Walk (Modified)")') }).first();
  await skillRowMod.hover();
  await skillRowMod.getByLabel('Delete skill').click();

  await expect(page.locator('h3:text("Walk (Modified)")')).not.toBeVisible();
  // Check "0 skills" text
  const gradeItemZero = page.locator('div').filter({ hasText: 'Level 1' }).filter({ hasText: '0 skills' });
  await expect(gradeItemZero.first()).toBeVisible();
});
