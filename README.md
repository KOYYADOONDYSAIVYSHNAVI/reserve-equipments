# API-ify the Reserve the Equipments System

## Overview
Created an API-enabled version of the reservation system that we've already worked on. Used FastAPI, which allows you to write API applications fairly easily. 

## Source Code Management
For code management we followed a process that allowed for us to complete our work without running into source code conflicts. We created a develop branch that is used to be the final product that we make a PR to main from. This branch is up to date with all of our work, with us making PRs from our individual branches to develop. We each created branches with our names just so that we could distinguish which branch we were working on. We discussed creating different branches for each feature, but we felt with the time constraints this week one branch each was more manageable for complexity. For the PRs into develop, we tried to have it so other people have a chance to review the PR before accepting it. This wasn't always feasible base on our timeline but we did have the chance to look over a few. There was some messiness in the commits at the beginning because there was a bit of a conflict between the develop and one our working branches. I also mistakenly accepted a PR into main instead of develop, so we had to revert that which also caused some extra commits to get everything up to date.

## API Design
We chose to create the API with the paths /reservation, /reservation/{id}, and /transactions. because we felt that these were the most concise choices for paths that we could make while also fulfilling all of the requirements. The reservation path was for seeing all reservations, ensure that reservations don't overlap, and give all the reservations for a time period. The /reservation/{id} is used for deleting the reseverations. /transactions is for the extra functionality that lists all the transactions in a date range.

# Security Discussion
### Password Storage and Hashing
The implementation employs PBKDF2-HMAC-SHA256 for password hashing. 

### Salting for Password Hashing
In the provided code, salts are employed for password hashing to enhance security. When a user registers, a unique salt is generated using `os.urandom(32)` for each user. This salt is then combined with the user's password before hashing using the PBKDF2-HMAC-SHA256 algorithm. Salts ensure that even if two users have the same password, their hashed passwords will be different due to the unique salt applied to each. This adds an extra layer of security. Moreover, the salts are stored alongside the hashed passwords in the database, enabling the system to verify passwords during login by applying the same salt to the provided password before hashing for comparison with the stored hashed password. This usage of salts strengthens the overall security of the password storage mechanism.


### Password Policy Enforcement
The function `is_temporary_password(password)` checks if a password is temporary and prompts the user to change it. However, there's no explicit enforcement of password complexity rules (e.g., minimum length, character requirements), which might weaken overall system security. Implementing and enforcing a strong password policy can enhance resilience against brute-force and dictionary attacks.

### Error Handling
The implementation includes error messages for invalid roles, duplicate usernames, and incorrect login credentials, which is beneficial for user feedback. 


## Description of design
## How to run and use the project
### Starting the Server
1. Navigate to the `api` folder in your terminal.
2. Run the following command to start the server using 
    ```
    uvicorn api:app
    ```
### Starting the Client
1. Navigate to the `views` folder in your terminal.
2. Run the following command to start the client application:
    ```
    python app.py
    ```
### Preloading Data
If you want to populate the database with preloaded data:
1. Open a new terminal window.
2. Navigate to the `database` folder.
3. Run the following command:
    ```
    python preloaded_data.py
    ```
### Running from Scratch
If you need to reset the database and start from scratch:
1. Navigate to the `database` folder in your terminal.
2. Run the following command to delete existing data:
    ```
    python delete_data.py
    ```
3. Start the client and server as described above.

### Using the Application
Once the server and client are running:
- You can register new users, login with existing credentials, and perform password changes from the client interface.

## How to run tests
## Passwords for sample users
1. **Username**: customer1
   - **Password**: customer1@

2. **Username**: customer2
   - **Password**: customer2@

3. **Username**: admin1
   - **Password**: admin1$

4. **Username**: admin2
   - **Password**: admin2$

5. **Username**: scheduler1
   - **Password**: scheduler1!

6. **Username**: scheduler2
   - **Password**: scheduler2!

## How to see the log operations
1. Navigate to back to the `views` folder in your terminal.
2. Run the following command to start the client application:
    ```
    python app.py
    ```
3. Register and login as an admin by following the prompt
4. Select the "5. Display Operation History" option to view a printout of all log operations

## Issues
Tests for login operations are failing to pass. Some reorganization needs to happen with how the databases are invoked.


