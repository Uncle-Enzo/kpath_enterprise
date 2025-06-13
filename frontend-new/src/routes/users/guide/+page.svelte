<script lang="ts">
  import { isAdmin } from '$lib/stores/auth';
  import Fa from 'svelte-fa';
  import { 
    faBook, faUsers, faUserShield, faPlus, faEdit, faToggleOn, faTrash,
    faExclamationTriangle, faCheckCircle, faLock, faEye, faCog 
  } from '@fortawesome/free-solid-svg-icons';
</script>

{#if !$isAdmin}
  <div class="max-w-2xl mx-auto">
    <div class="card">
      <p class="text-red-500">Access denied. Admin privileges required.</p>
      <div class="mt-4">
        <a href="/users" class="text-primary-600 hover:text-primary-800">← Back to Users</a>
      </div>
    </div>
  </div>
{:else}
  <div class="max-w-4xl mx-auto space-y-8">
    <!-- Header -->
    <div class="flex justify-between items-start">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">User Management Guide</h1>
        <p class="text-lg text-gray-600">Complete guide to managing users in KPATH Enterprise</p>
      </div>
      <div class="flex space-x-3">
        <a href="/users" class="btn btn-secondary">
          <Fa icon={faUsers} class="mr-2" />
          Manage Users
        </a>
        <a href="/users/new" class="btn btn-primary">
          <Fa icon={faPlus} class="mr-2" />
          Create User
        </a>
      </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <a href="/users" class="card hover:shadow-lg transition-shadow cursor-pointer">
        <div class="flex items-center space-x-3">
          <div class="bg-blue-100 p-3 rounded-lg">
            <Fa icon={faUsers} class="text-blue-600 text-xl" />
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">View All Users</h3>
            <p class="text-sm text-gray-600">Manage existing user accounts</p>
          </div>
        </div>
      </a>
      
      <a href="/users/new" class="card hover:shadow-lg transition-shadow cursor-pointer">
        <div class="flex items-center space-x-3">
          <div class="bg-green-100 p-3 rounded-lg">
            <Fa icon={faPlus} class="text-green-600 text-xl" />
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">Create New User</h3>
            <p class="text-sm text-gray-600">Add a new user to the system</p>
          </div>
        </div>
      </a>
      
      <div class="card">
        <div class="flex items-center space-x-3">
          <div class="bg-purple-100 p-3 rounded-lg">
            <Fa icon={faUserShield} class="text-purple-600 text-xl" />
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">Admin Access</h3>
            <p class="text-sm text-gray-600">Full user management privileges</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Overview -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Overview</h2>
      <p class="text-gray-600 mb-6">
        The KPATH Enterprise User Management system provides comprehensive tools for managing system users, their roles, 
        and access permissions. As an administrator, you have full control over user accounts and security settings.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 class="font-medium text-gray-900 mb-3">Key Features</h3>
          <ul class="space-y-2 text-sm text-gray-600">
            <li class="flex items-center"><Fa icon={faCheckCircle} class="text-green-500 mr-2" /> Create and manage user accounts</li>
            <li class="flex items-center"><Fa icon={faCheckCircle} class="text-green-500 mr-2" /> Assign and modify user roles</li>
            <li class="flex items-center"><Fa icon={faCheckCircle} class="text-green-500 mr-2" /> Control user access and permissions</li>
            <li class="flex items-center"><Fa icon={faCheckCircle} class="text-green-500 mr-2" /> Activate and deactivate accounts</li>
            <li class="flex items-center"><Fa icon={faCheckCircle} class="text-green-500 mr-2" /> Secure password management</li>
          </ul>
        </div>
        
        <div>
          <h3 class="font-medium text-gray-900 mb-3">Security Features</h3>
          <ul class="space-y-2 text-sm text-gray-600">
            <li class="flex items-center"><Fa icon={faLock} class="text-blue-500 mr-2" /> Admin-only access control</li>
            <li class="flex items-center"><Fa icon={faLock} class="text-blue-500 mr-2" /> Secure password hashing</li>
            <li class="flex items-center"><Fa icon={faLock} class="text-blue-500 mr-2" /> Role-based permissions</li>
            <li class="flex items-center"><Fa icon={faLock} class="text-blue-500 mr-2" /> User activity monitoring</li>
            <li class="flex items-center"><Fa icon={faLock} class="text-blue-500 mr-2" /> Account status management</li>
          </ul>
        </div>
      </div>
    </div>
    
    <!-- User Roles -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">User Roles and Permissions</h2>
      <p class="text-gray-600 mb-6">
        KPATH Enterprise uses role-based access control (RBAC) with four distinct user roles:
      </p>
      
      <div class="space-y-4">
        <!-- Administrator -->
        <div class="border border-red-200 rounded-lg p-4 bg-red-50">
          <div class="flex items-center space-x-3 mb-3">
            <div class="bg-red-100 p-2 rounded-lg">
              <Fa icon={faUserShield} class="text-red-600" />
            </div>
            <div>
              <h3 class="font-semibold text-red-900">Administrator</h3>
              <p class="text-sm text-red-700">Full System Access</p>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p class="font-medium text-red-800 mb-2">Permissions:</p>
              <ul class="space-y-1 text-red-700">
                <li>• Manage all users and roles</li>
                <li>• Configure system settings</li>
                <li>• Access all services and data</li>
                <li>• View system analytics</li>
              </ul>
            </div>
            <div>
              <p class="font-medium text-red-800 mb-2">Use Cases:</p>
              <ul class="space-y-1 text-red-700">
                <li>• System administrators</li>
                <li>• IT managers</li>
                <li>• DevOps engineers</li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Editor -->
        <div class="border border-blue-200 rounded-lg p-4 bg-blue-50">
          <div class="flex items-center space-x-3 mb-3">
            <div class="bg-blue-100 p-2 rounded-lg">
              <Fa icon={faEdit} class="text-blue-600" />
            </div>
            <div>
              <h3 class="font-semibold text-blue-900">Editor</h3>
              <p class="text-sm text-blue-700">Service Management Access</p>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p class="font-medium text-blue-800 mb-2">Permissions:</p>
              <ul class="space-y-1 text-blue-700">
                <li>• Create and edit services</li>
                <li>• Manage service configurations</li>
                <li>• Import service data</li>
                <li>• Use search features</li>
              </ul>
            </div>
            <div>
              <p class="font-medium text-blue-800 mb-2">Use Cases:</p>
              <ul class="space-y-1 text-blue-700">
                <li>• Service architects</li>
                <li>• API managers</li>
                <li>• Integration specialists</li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Viewer -->
        <div class="border border-green-200 rounded-lg p-4 bg-green-50">
          <div class="flex items-center space-x-3 mb-3">
            <div class="bg-green-100 p-2 rounded-lg">
              <Fa icon={faEye} class="text-green-600" />
            </div>
            <div>
              <h3 class="font-semibold text-green-900">Viewer</h3>
              <p class="text-sm text-green-700">Read-Only Access</p>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p class="font-medium text-green-800 mb-2">Permissions:</p>
              <ul class="space-y-1 text-green-700">
                <li>• View all services</li>
                <li>• Use search features</li>
                <li>• Access documentation</li>
                <li>• View configurations</li>
              </ul>
            </div>
            <div>
              <p class="font-medium text-green-800 mb-2">Use Cases:</p>
              <ul class="space-y-1 text-green-700">
                <li>• Developers</li>
                <li>• Business analysts</li>
                <li>• Project managers</li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- User -->
        <div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
          <div class="flex items-center space-x-3 mb-3">
            <div class="bg-gray-100 p-2 rounded-lg">
              <Fa icon={faUsers} class="text-gray-600" />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">User</h3>
              <p class="text-sm text-gray-700">Basic Access</p>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p class="font-medium text-gray-800 mb-2">Permissions:</p>
              <ul class="space-y-1 text-gray-700">
                <li>• Search for services</li>
                <li>• View basic information</li>
                <li>• Access own profile</li>
                <li>• Limited system access</li>
              </ul>
            </div>
            <div>
              <p class="font-medium text-gray-800 mb-2">Use Cases:</p>
              <ul class="space-y-1 text-gray-700">
                <li>• End users</li>
                <li>• External stakeholders</li>
                <li>• Limited access accounts</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User Management Tasks -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Common User Management Tasks</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Creating Users -->
        <div>
          <h3 class="font-medium text-gray-900 mb-3 flex items-center">
            <Fa icon={faPlus} class="text-green-600 mr-2" />
            Creating New Users
          </h3>
          <ol class="space-y-2 text-sm text-gray-600">
            <li><strong>1.</strong> Navigate to Users → Create New User</li>
            <li><strong>2.</strong> Fill out the user form with required information</li>
            <li><strong>3.</strong> Select appropriate role based on user needs</li>
            <li><strong>4.</strong> Set secure password (minimum 8 characters)</li>
            <li><strong>5.</strong> Submit to create the user account</li>
          </ol>
          <div class="mt-3 p-3 bg-blue-50 rounded-lg">
            <p class="text-xs text-blue-800">
              <Fa icon={faExclamationTriangle} class="mr-1" />
              Remember: Use the principle of least privilege when assigning roles
            </p>
          </div>
        </div>
        
        <!-- Editing Users -->
        <div>
          <h3 class="font-medium text-gray-900 mb-3 flex items-center">
            <Fa icon={faEdit} class="text-blue-600 mr-2" />
            Editing Existing Users
          </h3>
          <ol class="space-y-2 text-sm text-gray-600">
            <li><strong>1.</strong> Find the user in the Users list</li>
            <li><strong>2.</strong> Click the edit icon next to their name</li>
            <li><strong>3.</strong> Update user information as needed</li>
            <li><strong>4.</strong> Change password if required (optional)</li>
            <li><strong>5.</strong> Save changes to update the account</li>
          </ol>
          <div class="mt-3 p-3 bg-green-50 rounded-lg">
            <p class="text-xs text-green-800">
              <Fa icon={faCheckCircle} class="mr-1" />
              Tip: You can change user roles at any time based on their evolving needs
            </p>
          </div>
        </div>
        
        <!-- Managing Status -->
        <div>
          <h3 class="font-medium text-gray-900 mb-3 flex items-center">
            <Fa icon={faToggleOn} class="text-purple-600 mr-2" />
            Managing User Status
          </h3>
          <div class="space-y-3 text-sm text-gray-600">
            <div>
              <p class="font-medium text-gray-800">Activating Users:</p>
              <p>Active users can log in and use the system normally</p>
            </div>
            <div>
              <p class="font-medium text-gray-800">Deactivating Users:</p>
              <p>Inactive users cannot log in but their data is preserved</p>
            </div>
          </div>
          <div class="mt-3 p-3 bg-yellow-50 rounded-lg">
            <p class="text-xs text-yellow-800">
              <Fa icon={faExclamationTriangle} class="mr-1" />
              Recommended: Deactivate instead of deleting users who may return
            </p>
          </div>
        </div>
        
        <!-- Security -->
        <div>
          <h3 class="font-medium text-gray-900 mb-3 flex items-center">
            <Fa icon={faLock} class="text-red-600 mr-2" />
            Security Best Practices
          </h3>
          <ul class="space-y-2 text-sm text-gray-600">
            <li>• Regularly review user accounts and permissions</li>
            <li>• Use strong passwords (8+ characters)</li>
            <li>• Deactivate accounts for users who no longer need access</li>
            <li>• Monitor user activity for suspicious behavior</li>
            <li>• Keep user information up to date</li>
          </ul>
          <div class="mt-3 p-3 bg-red-50 rounded-lg">
            <p class="text-xs text-red-800">
              <Fa icon={faExclamationTriangle} class="mr-1" />
              Security: Never share admin credentials or create unnecessary admin accounts
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Troubleshooting -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Common Issues & Solutions</h2>
      
      <div class="space-y-4">
        <div class="border-l-4 border-red-500 pl-4">
          <h3 class="font-medium text-gray-900">❌ "User with this email already exists"</h3>
          <p class="text-sm text-gray-600 mt-1">
            This email is already registered. Check if the user exists or use a different email address.
          </p>
        </div>
        
        <div class="border-l-4 border-yellow-500 pl-4">
          <h3 class="font-medium text-gray-900">⚠️ "Access denied. Admin privileges required"</h3>
          <p class="text-sm text-gray-600 mt-1">
            Only administrators can manage users. Ensure you're logged in with admin privileges.
          </p>
        </div>
        
        <div class="border-l-4 border-blue-500 pl-4">
          <h3 class="font-medium text-gray-900">ℹ️ User cannot log in</h3>
          <p class="text-sm text-gray-600 mt-1">
            Check if the user account is active and verify their email/password credentials.
          </p>
        </div>
        
        <div class="border-l-4 border-green-500 pl-4">
          <h3 class="font-medium text-gray-900">✅ Password requirements not met</h3>
          <p class="text-sm text-gray-600 mt-1">
            Passwords must be at least 8 characters long. Use a mix of letters, numbers, and symbols.
          </p>
        </div>
      </div>
    </div>
    
    <!-- Quick Actions Footer -->
    <div class="card bg-gray-50">
      <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
      <div class="flex flex-wrap gap-3">
        <a href="/users" class="btn btn-secondary">
          <Fa icon={faUsers} class="mr-2" />
          View All Users
        </a>
        <a href="/users/new" class="btn btn-primary">
          <Fa icon={faPlus} class="mr-2" />
          Create New User
        </a>
      </div>
    </div>
    
    <!-- Footer -->
    <div class="text-center py-8 border-t">
      <p class="text-gray-500 text-sm">
        KPATH Enterprise User Management Guide v1.0
      </p>
      <div class="mt-2">
        <a href="/users" class="text-primary-600 hover:text-primary-800 text-sm">← Back to User Management</a>
      </div>
    </div>
  </div>
{/if}