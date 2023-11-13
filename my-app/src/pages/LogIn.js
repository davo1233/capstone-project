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
import React from "react";

export default function LogIn() {
  // When the user submits their login details
  const handleSubmit = async (event) => {
    // The username is retrieved and saved into the frontend storage.
    const username = document.getElementById("username").value;
    sessionStorage.setItem("username", username);

    // Fetch function to post the login details
    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: { "Content-Type" : "application/json"},
      body: JSON.stringify({
        "username" : username,
        "password" : document.getElementById("password").value
      })
    })
    if (response.ok) {
      // Upon successful log in, the token passed back is saved to the frontend storage.
      const token = await response.json()
      sessionStorage.setItem("token", JSON.stringify(token)) 
      
      // The user is redirected to their dashboard after loggin in.
      window.location.href = "http://localhost:3000/dashboard";
    } else {
      // Upon failed login, the user is alerted that the details did not match our records.
      document.getElementById("message").innerHTML = "Username and password do not match.";
    }
  }

  return (
    <form>
      <Stack>
        <InputGroup size="md">
          <InputLeftAddon width="110px" children="Username" />
          <Input
            pr="4.5rem"
            type="text"
            id="username"
          />
        </InputGroup>
        <PasswordInput />
        <Divider/>
        <Button onClick={handleSubmit}>Log In</Button>
      </Stack>
      <Text id="message"></Text>
    </form>
  )
}

function PasswordInput() {
  const [show, setShow] = React.useState(false)
  const handleClick = () => setShow(!show)
  return (
    <InputGroup size='md'>
      <InputLeftAddon width="110px" children="Password" />
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