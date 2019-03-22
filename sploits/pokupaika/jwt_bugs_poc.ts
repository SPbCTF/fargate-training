import fs from "fs";
import jwt from "jsonwebtoken";

// Read ec key
const ecPriv = fs.readFileSync("./secrets/private.pem");
const ecPub = fs.readFileSync("./secrets/private.pem");

const jwt_ec = jwt.sign({ classified: "kek" }, ecPriv, { algorithm: "ES256" });

const jwt_hmac = jwt.sign({ classified: "kek" }, ecPub, {
  algorithm: "HS256",
});

const jwt_none = jwt.sign({ classified: "kek" }, ecPub, { algorithm: "none" });

const jwts = { jwt_ec, jwt_hmac, jwt_none };

for (const [key, value] of Object.entries(jwts)) {
  console.log(key);
  console.log(value);
  try {
    console.log(
      jwt.verify(value, ecPub, { algorithms: ["none", "HS256", "ES256"] }),
    );
  } catch (e) {
    console.log(
      jwt.verify(value, "", { algorithms: ["none", "HS256", "ES256"] }),
    );
  }
  console.log("");
}
