import uuid from "uuid";

const apiPrefix = "/api";
// the password is global for every user, since authentication is purely based
// on randomly generated fake email addresses
const password = "softweeere";

const getRandomString = () => uuid.v4();


async function register() {
    return new Promise(((resolve, reject) => {
        const email = `${getRandomString()}@example.com`;
        fetch(`${apiPrefix}/auth/register`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email: email, password: password})
        })
            .then(res => {
                if (res.ok)
                    resolve(res.json());
                else if (res.status === 400)
                    reject(`User ${email} already registered`)
                else if (res.status === 422)
                    reject("Validation error")
            })
            .catch(err => reject(err));
    }));
}

async function isLoggedIn() {
    return new Promise(((resolve, reject) => {

    }));
}

const API = {register};
export default API;