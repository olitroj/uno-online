failed_tests=0

function pass() {
    echo -e "  $1 - \033[0;32mPASS\033[0m"
}

function fail() {
    echo -e "  $1 - \033[0;31mFAIL\033[0m"
    failed_tests++
}

function assert_eq() {
    if [[ "$2" == $3 ]]; then
        pass "$1"
    else
        fail "$1"
        echo "$result"
    fi
}

function assert_neq() {
    if [[ "$2" != $3 ]]; then
        pass "$1"
    else
        fail "$1"
        echo "$result"
    fi
}

function assert_null() {
    if [[ -z "$2" ]]; then
        pass "$1"
    else
        fail "$1"
        echo "$result"
    fi
}

function assert_not_null() {
    if [[ -n "$2" ]]; then
        pass "$1"
    else
        fail "$1"
        echo "$result"
    fi
}

function code() {
    head -n1 <<< "$result" | cut -d" " -f2
}

function header() {
    grep -i "$1" <<< "$result" | cut -d" " -f2-
}

function body() {
    sed "1,/^$/d" <<< "$result"
}



# POST /account
header="Content-Type: application/x-www-form-urlencoded"

result=$(curl -s -i -X POST -H "$header" -d 'username=oliver&password=12345' $HOST_NAME/account)
assert_eq "Code 201" "$(code)" 201
assert_eq "Set cookie" "$(header set-cookie)" "access_token=*"
assert_null "Empty Body" "$(body)"

token="$(header set-cookie)"

result=$(curl -s -i -X POST -H "$header" -d 'username=oliver&password=12345' $HOST_NAME/account)
assert_eq "Code 409" "$(code)" 409
assert_null "No cookie" "$(header set-cookie)"

result=$(curl -s -i -X POST -H "$header" -d 'sfsdfesa' $HOST_NAME/account)
assert_eq "Code 422" "$(code)" 422
assert_null "No cookie" "$(header set-cookie)"


# GET /account/statistics
header="cookie: $token"

result=$(curl -s -i -X GET -H "$header" $HOST_NAME/account/statistics)
assert_eq "Code 200" "$(code)" 200
assert_eq "JSON body" "$(header content-type)" "application/json"
assert_eq "Correct response body" "$(body)" "{\"account_username\":\"oliver\",\"status\":\"offline\",\"description\":null,\"wins\":0,\"losses\":0}"

result=$(curl -s -i -X GET -H "cookie: sljfoasenm" $HOST_NAME/account/statistics)
assert_eq "Code 401" "$(code)" 401
assert_neq "No response body" "$(body)" "{\"status\":\"oliver\",\"status\":\"offline\",\"description\":null,\"wins\":0,\"losses\":0}"


# POST /token
header="Content-Type: application/x-www-form-urlencoded"

result=$(curl -s -i -X POST -H "$header" -d 'username=oliver&password=12345' $HOST_NAME/token)
assert_eq "Code 201" "$(code)" 201
assert_eq "Set cookie" "$(header set-cookie)" "access_token=*"
assert_null "Empty Body" "$(body)"

result=$(curl -s -i -X POST -H "$header" -d 'username=oliver&password=56789' $HOST_NAME/token)
assert_eq "Code 401" "$(code)" 401
assert_null "No cookie" "$(header set-cookie)"

result=$(curl -s -i -X POST -H "$header" -d 'sdfasefsdfs' $HOST_NAME/token)
assert_eq "Code 422" "$(code)" 422
assert_null "No cookie" "$(header set-cookie)"


# DELETE /token
result=$(curl -s -i -X DELETE -H "$header" $HOST_NAME/token)
assert_eq "Code 204" "$(code)" 204
assert_eq "Unset cookie" "$(header set-cookie)" "access_token=\"\"*"

echo "----------------------------"
echo "Failed tests: $failed_tests"
echo "----------------------------"