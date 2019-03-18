## Check

1. Get pubkey
2. Register
3. Verify jwt
4. New zakupka
5. Get new zakupka
6. Check if in new users

## Put vuln 1

1. Register with secret=flag

## Put vuln 2

1. Register
2. New zakupka with accessLevel!=0 and description=flag

## Get vuln 1

1. Login with creds
2. Check flag in /me

## Get vuln 2

1. Login with creds
2. Check flag in zakupka
