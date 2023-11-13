import {
  Box,
  Button,
  ChakraProvider,
  Grid,
  Image,
  Stack,
  Text,
  theme,
  VStack
} from '@chakra-ui/react';
import { Outlet } from "react-router-dom";

import { ColorModeSwitcher } from './../components/ColorModeSwitcher';
import img from "./../images/main_page.png"

const Home = () => {
  const handleCreateAccountButtonClicked = (event) => {
    window.location.href = "http://localhost:3000/createaccount";
  }

  const handleLogInButtonClicked = (event) => {
    window.location.href = "http://localhost:3000/login";
  }

  return (
    <ChakraProvider theme={theme}>
      <Box textAlign="center" fontSize="xl">
        <Grid minH="100vh" p={3}>
          <ColorModeSwitcher justifySelf="flex-end" />
          <VStack spacing={8}>
            <Image width="100px" src={img}></Image>
            
            <Text>
              Welcome to ObservANT Task Manager
            </Text>
            <Stack spacing={4} direction='row' align='center'>
              <Button onClick={handleCreateAccountButtonClicked}>Create Account</Button> 
              <Button onClick={handleLogInButtonClicked}>Log In</Button>
            </Stack>
            <Outlet />
        </VStack>
        </Grid>
      </Box>
    </ChakraProvider>
  );
};
  
export default Home;