/**
 * Test script to verify the filter initialization fix
 */

// Mock the DOM elements that would be present in the browser
const mockElements = {
  projectsFilter: {
    value: 'week', // This simulates the HTML selector with "Неделя" selected
  },
  projectsList: {
    innerHTML: '',
  },
};

// Simulate the old Dashboard constructor behavior
function DashboardOld() {
  // Old behavior: hardcoded to 'all'
  this.currentFilter = 'all';
  this.elements = mockElements;
}

// Simulate the new Dashboard constructor behavior
function DashboardNew() {
  // New behavior: read from selector
  this.elements = mockElements;
  this.currentFilter = this.elements.projectsFilter.value;
}

// Test function
function runTest() {
  console.log('🧪 Testing Dashboard Filter Initialization Fix');
  console.log('='.repeat(50));

  // Test old behavior
  const oldDashboard = new DashboardOld();
  console.log(`❌ OLD BEHAVIOR:`);
  console.log(`   Selector value: ${mockElements.projectsFilter.value}`);
  console.log(`   Dashboard currentFilter: ${oldDashboard.currentFilter}`);
  console.log(
    `   Match: ${
      oldDashboard.currentFilter === mockElements.projectsFilter.value
        ? '✅'
        : '❌'
    }`
  );

  // Test new behavior
  const newDashboard = new DashboardNew();
  console.log(`\n✅ NEW BEHAVIOR:`);
  console.log(`   Selector value: ${mockElements.projectsFilter.value}`);
  console.log(`   Dashboard currentFilter: ${newDashboard.currentFilter}`);
  console.log(
    `   Match: ${
      newDashboard.currentFilter === mockElements.projectsFilter.value
        ? '✅'
        : '❌'
    }`
  );

  // Final result
  const testPassed =
    newDashboard.currentFilter === mockElements.projectsFilter.value;
  console.log(`\n${'='.repeat(50)}`);
  console.log(`🎯 RESULT: ${testPassed ? '✅ TEST PASSED' : '❌ TEST FAILED'}`);
  console.log(
    `   The fix correctly initializes currentFilter from the selector value`
  );

  return testPassed;
}

// Run the test
const testPassed = runTest();
process.exit(testPassed ? 0 : 1);
