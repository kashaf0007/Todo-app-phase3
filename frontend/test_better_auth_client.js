/**
 * Test script to verify Better Auth client configuration
 */
import { authClient } from './src/lib/auth-client';

function testBetterAuthClientConfig() {
  console.log('Testing Better Auth client configuration...');
  
  try {
    // Test that authClient object exists
    if (!authClient) {
      throw new Error('authClient is undefined');
    }
    
    // Test that authClient has required methods
    if (typeof authClient.signIn === 'undefined') {
      throw new Error('authClient.signIn method is missing');
    }
    
    if (typeof authClient.signOut === 'undefined') {
      throw new Error('authClient.signOut method is missing');
    }
    
    if (typeof authClient.getSession === 'undefined') {
      throw new Error('authClient.getSession method is missing');
    }
    
    console.log('✓ Better Auth client configuration is valid');
    console.log('✓ All required methods are available');
    
    return true;
  } catch (error) {
    console.error(`✗ Error testing Better Auth client configuration: ${error.message}`);
    return false;
  }
}

// Run the test
const success = testBetterAuthClientConfig();
if (success) {
  console.log('\n✓ Better Auth client configuration test PASSED');
} else {
  console.log('\n✗ Better Auth client configuration test FAILED');
}