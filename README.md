# virtual-wallet-app
A platform that enables users to manage their finances by depositing, transferring, and withdrawing funds. Coupled with spending analytics, this system categorizes expenses and provides insights to help users track and manage their money more effectively.


```bash
Directory structure:
└── mwangi-george-virtual-wallet-app/
    ├── README.md
    ├── LICENSE
    ├── requirements.txt
    ├── alembic/
    │   ├── README
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │       ├── 2585a48ad15b_removed_tasks_table.py
    │       ├── 67939c9a8eac_creating_first_tables.py
    │       └── 7b313d98d94d_changed_details_column_from_json_to_str.py
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── database.py
    │   │   ├── emails.py
    │   │   ├── logs.py
    │   │   └── security.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   └── models.py
    │   ├── routes/
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── analytics.py
    │   │   ├── auth.py
    │   │   ├── user.py
    │   │   └── wallet.py
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── analytics.py
    │   │   ├── auth.py
    │   │   ├── user.py
    │   │   └── wallet.py
    │   └── services/
    │       ├── __init__.py
    │       ├── admin.py
    │       ├── analytics.py
    │       ├── auth.py
    │       ├── user.py
    │       └── wallet.py
    └── templates/
        ├── password_update_confirm.html
        ├── update_user_password_form.html
        └── verification_success.html
```
