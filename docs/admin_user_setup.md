# Admin User Setup

## Default Admin Credentials

The admin user has been set up with the following credentials:

- **Email**: admin@kpath.ai
- **Password**: 1234rt4rd
- **Role**: admin

## How to Login

1. Start the application:
   ```bash
   ./restart.sh
   ```

2. Open the frontend at http://localhost:5173

3. Use the admin credentials above to login

## Managing Users

To create or update the admin user in the future:

```bash
cd /Users/james/claude_development/kpath_enterprise
source venv/bin/activate
python scripts/setup_admin_user.py
```

The script will:
- Create the admin user if it doesn't exist
- Update the password if the user already exists
- Ensure the user has admin role and is active

## Security Note

Please remember to change the default password in production environments!
