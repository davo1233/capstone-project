import {
    Avatar,
    Box,
    Button,
    HStack,
    Image,
    Stack,
    Text,
} from '@chakra-ui/react';
import { formatDistanceToNow } from "date-fns";
import React, { useEffect, useState } from "react";

import ant_black from "./../images/ant_black.png";

export function Notifications({ isOpen }) {
    // If the user token cannot be found, we return back to the home page.
    if (!JSON.parse(sessionStorage.getItem("token"))) {
		window.location.href = "http://localhost:3000";
	}
    const token = JSON.parse(sessionStorage.getItem("token")).access_token;

    // Some states for showing notifications
    const [notifications, setNotifications] = useState([]);
    const [hiddenNotifications, setHiddenNotifications] = useState([]);
    const [connectionRequests, setConnectionRequests] = useState([]);
    const [accept, setAccept] = useState([]);

    const fetchNotifications = async () => {
        const response1 = await fetch("http://localhost:8000/connections/requests/incoming?" + new URLSearchParams({"token" : token}).toString()); 
        if (response1.ok) {
            const cr_response = await response1.json();
            setConnectionRequests(cr_response);
        }

        const response2 = await fetch("http://localhost:8000/notifications?" + new URLSearchParams({"token" : token}).toString());
        if (response2.ok) {
            const notif_response = await response2.json()
            
            // We reverse the notifications to have the most recent one at the head.
            const notif_response_reversed = notif_response.slice().reverse();
            
            // The first 10 notifications will be shown only initially.
            if (notif_response.length <= 10) {
                setNotifications(notif_response_reversed)
            } else {
                setNotifications(notif_response_reversed.slice(0, 10))
                
                // The rest we hide them for now.
                setHiddenNotifications(notif_response_reversed.slice(10, notif_response.length))
            }
        }
    }
    
    // Every time the isOpen state is changed to true, we fetch the notifications.
    useEffect(() => {
        if (isOpen) {
            fetchNotifications();
        }
      }, [isOpen]);

    // Acceping a connection request - putting changed details to the backend.
    function handleAcceptClicked(c_id) {
        fetch(`http://localhost:8000/connections/requests/${c_id}/accept`, {
            method: "PUT",
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify({
                "connection_id" : c_id,
                "token" : token
            })
        }).then((response) => {
            if (response.ok) {
                console.log("Accepted.")
            }
        })
        setAccept(true);

        // We hide the accept/decline buttons and show a message saying that the message has been sent.
        document.getElementById(c_id + "_result").hidden = false;
        document.getElementById(c_id + "_accept_button").hidden = true;
        document.getElementById(c_id + "_reject_button").hidden = true;

    }

    function handleDeclineClicked(c_id) {
        fetch(`http://localhost:8000/connections/requests/${c_id}/decline`, {
            method: "DELETE",
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify({
                "connection_id" : c_id,
                "token" : token
            })
        }).then((response) => {
            if (response.ok) {
                console.log("Declined.")
            }
        })
        setAccept(false);
        document.getElementById(c_id + "_result").hidden = false;
        document.getElementById(c_id + "_accept_button").hidden = true;
        document.getElementById(c_id + "_reject_button").hidden = true;

    }

    // Given username it will try to find the source of the profile ant image.
    function findAntImageSrc(username) {
		if (JSON.parse(localStorage.getItem("userAntColours")) == null) {
			return ant_black
		}
		if (JSON.parse(localStorage.getItem("userAntColours"))[username] === undefined) {
			return ant_black
		}
		return JSON.parse(localStorage.getItem("userAntColours"))[username];
	}

    // Setting the maximum height of the notificaiton popover message so it doesn't go over the window height.
    const maxHeight = `${window.innerHeight - 200}px`;

    // When the user presses to load more notifictaions, the next 5 are shown.
    const handleLoadMore = (event) => {
        if (hiddenNotifications.length <= 5) {
            console.log(hiddenNotifications)
            setNotifications([...notifications, ...hiddenNotifications.slice(0, hiddenNotifications.length)]);
            setHiddenNotifications([])
        } else {
            console.log([...notifications, ...hiddenNotifications.slice(0, 5)])
            setNotifications([...notifications, ...hiddenNotifications.slice(0, 5)]);
            setHiddenNotifications(hiddenNotifications.slice(5, hiddenNotifications.length))
        }
        
    };

    return (
        <Stack style={{maxHeight: maxHeight, overflowY:"scroll"}}>
            <Text hidden={connectionRequests.length === 0}>Connection request from: </Text>
            {connectionRequests.map((request) => ( 
                <Box spacing={5} borderWidth="1px" padding="10px">
                    <HStack>
                        <Image boxSize="64px" src={findAntImageSrc(request.sender_username)}/>
                        <Text>{request.sender_username}</Text>
                    </HStack>
                    <HStack>
                        <Button onClick={() => window.location.href = `http://localhost:3000/profile/${request.sender_username}`}>View Profile</Button>
                        <Button id={request.connection_id + "_accept_button"} onClick={() => handleAcceptClicked(request.connection_id)}>Accept</Button>
                        <Button id={request.connection_id + "_reject_button"} onClick={() => handleDeclineClicked(request.connection_id)}>Decline</Button>
                        <Text hidden id={request.connection_id + "_result"}>Request {accept ? "accepted." : "declined."}</Text>
                    </HStack>
                </Box>
            ))}
            {notifications.map((notification) => (
                <Box 
                    spacing={5} 
                    borderWidth="1px" 
                    padding="10px" 
                    _hover={{textDecoration: "underline"}}
                    cursor="pointer"
                    onClick={() => window.location.href = `http://localhost:3000/project/${notification.type_id}`}
                >
                    <HStack>
                        <Avatar src={findAntImageSrc(notification.notifier)}></Avatar>
                        <Stack spacing="3px">
                            <Text>
                                {notification.message}{" "}
                                <Text as="span" color="grey">
                                    {formatDistanceToNow(new Date(notification.date_created), { addSuffix: true })}
                                </Text>
                            </Text>
                            <Text>{notification.project_title}</Text>
                        </Stack>
                    </HStack>
                </Box>
            ))}
            {hiddenNotifications.length > 0 && (
                <Button onClick={handleLoadMore}>Load More</Button>
            )}
        </Stack>
    )
}