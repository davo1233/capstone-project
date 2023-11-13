// Third-party libraries
import { BellIcon } from '@chakra-ui/icons';
import {
  Button,
  HStack,
  IconButton,
  Image,
  Popover,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  Spacer,
  Text
} from '@chakra-ui/react';
import React, { useState } from "react";
import { Link } from 'react-router-dom';

// Our own imports
import ant_black from "./../images/ant_black.png";
import { Notifications } from "./Notifications";

export const NavBar = () => {
  // This state checks if the notification Popover is opened or closed.
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  // If the notifications button is clicked the above state must change
  function handleNotificationsClick() {
    setNotificationsOpen((prevState) => !prevState);
  }

  return (
    <HStack padding="20px" spacing="1" justify="space-between">
        <Link to={"/"}>

            <Button variant="ghost">
              <HStack>
                <Image boxSize="32px"src={ant_black}/>
                <Text>ObservANT</Text>
              </HStack>
            </Button>
          </Link>
        <Link to={"/dashboard"}>
          <Button variant="ghost">Dashboard</Button>
        </Link>
        <Spacer/>
        <HStack spacing="3">
          <Popover placement="bottom-end" strategy="fixed">
            <PopoverTrigger>
              <IconButton icon={<BellIcon />} onClick={handleNotificationsClick}></IconButton>
            </PopoverTrigger>
            <PopoverContent width="450px" offset={[null, "0"]}>
              <PopoverCloseButton />
              <PopoverHeader>Notifications</PopoverHeader>
              <PopoverBody>
                <Notifications isOpen={notificationsOpen}/>
              </PopoverBody>
            </PopoverContent>
          </Popover>
          <Link to={`/profile/${sessionStorage.getItem("username")}`}>
            <Button variant="ghost">Account</Button>
          </Link>
          <Link to={"/"}>
            <Button variant="ghost">Logout</Button>
          </Link>
        </HStack>
    </HStack>
)
}