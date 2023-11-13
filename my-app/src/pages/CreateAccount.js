import {
  Button,
  Divider,
  Input,
  InputGroup,
  InputLeftAddon,
  InputRightElement,
  Stack,
  Text
} from "@chakra-ui/react";
import React from 'react';

import ant_black from "./../images/ant_black.png";

export default function CreateAccount() {
  // Handling the submission of the account creation.
  const handleSubmit = async (event) => {
    // Retrieve input data from the document.
    const password = document.getElementById("password").value;
    const cpassword = document.getElementById("cpassword").value;
    const username = document.getElementById("username").value;
   
    // Setting the current user's username on the frontend storage.
    sessionStorage.setItem("username", username);

    // Checking if password and confrim password inputs were the same.
    if (password === cpassword) {
      // Retreive all data and post the account to the backend.
      const newAccount = {
        "username" : username,
        "email" : document.getElementById("email").value,
        "firstname": document.getElementById("firstname").value,
        "lastname" : document.getElementById("lastname").value,
        "password" : password
      }

      const response = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newAccount)
      })

      if (response.ok) {
        // token is retrieved back from the fetch and is saved to the frontend storage.
        const token = await response.json()
        sessionStorage.setItem("token", JSON.stringify(token))
        
        // users are redirected to the dashboard after creating a new account
        window.location.href = "http://localhost:3000/dashboard";
      } else {
        // if fetch fails, we alert the user that the username is taken.
        document.getElementById("message").innerHTML = "Username already exists.";
      }
    }
  }

  return (
    <form>
      <Stack>
        <InputGroup size="md">
          <InputLeftAddon width="160px" children="First Name" />
          <Input
            pr="4.5rem"
            type="text"
            id="firstname"
          />
        </InputGroup>
        <InputGroup size="md">
          <InputLeftAddon width="160px" children="Last Name" />
          <Input
            pr="4.5rem"
            type="text"
            id="lastname"
          />
        </InputGroup>
        <InputGroup size="md">
          <InputLeftAddon width="160px" children="Email Address" />
          <Input
            pr="4.5rem"
            type="text"
            id="email"
          />
        </InputGroup>
        <InputGroup size="md">
          <InputLeftAddon width="160px" children="Username" />
          <Input
            pr="4.5rem"
            type="text"
            id="username"
          />
        </InputGroup>
        <PasswordInput />
        <CPasswordInput />
        <Divider/>
        <Button onClick={handleSubmit}>Register</Button>
      </Stack>
      <Text id="message"></Text>
      <p id="error"></p>
    </form>
  )
}

function PasswordInput() {
  const [show, setShow] = React.useState(false)
  const handleClick = () => setShow(!show)
  return (
    <InputGroup size='md'>
      <InputLeftAddon width="160px" children="Password" />
      <Input
        pr='4.5rem'
        type={show ? 'text' : 'password'}
        id="password"
      />
      <InputRightElement width='4.5rem'>
        <Button h='1.75rem' size='sm' onClick={handleClick}>
          {show ? 'Hide' : 'Show'}
        </Button>
      </InputRightElement>
    </InputGroup>
  )
}

function CPasswordInput() {
  const [show, setShow] = React.useState(false)
  const handleClick = () => setShow(!show)

  return (
    <InputGroup size='md'>
      <InputLeftAddon width="160px" children="Confirm Password" />
      <Input
        pr='4.5rem'
        type={show ? 'text' : 'password'}
        id="cpassword"
      />
      <InputRightElement width='4.5rem'>
        <Button h='1.75rem' size='sm' onClick={handleClick}>
          {show ? 'Hide' : 'Show'}
        </Button>
      </InputRightElement>
    </InputGroup>
  )
}