import { ArrowLeftIcon, ArrowRightIcon} from "@chakra-ui/icons"
import {
  Avatar, 
  Box,
  Button,
  ChakraProvider,
  Divider,
  Grid,
  HStack,
  IconButton,
  Image,
  Popover,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  Stack,
  Text,
  theme,
  VStack
} from '@chakra-ui/react';
import React, { useEffect, useState} from "react";

import { ColorModeSwitcher } from './../components/ColorModeSwitcher';
import { NavBar } from "./../components/NavBar";

import ant_black from "./../images/ant_black.png";
import ant_blue from "./../images/ant_blue.png";
import ant_green from "./../images/ant_green.png";
import ant_purple from "./../images/ant_purple.png";
import ant_red from "./../images/ant_red.png";
import ant_yellow from "./../images/ant_yellow.png";

import CHAD_1 from "./../images/CHAD-1.png";
import CHAD_2 from "./../images/CHAD-2.png";
import CHAD_3 from "./../images/CHAD-3.png";

export default function Profile() {
	// If token cannot be found, the user is returned back to the home page.
	if (!JSON.parse(sessionStorage.getItem("token"))) {
		window.location.href = "http://localhost:3000";
	}
	const token = JSON.parse(sessionStorage.getItem("token")).access_token;
	
	// Ther username is retrieved from the URL.
	const username = window.location.href.split("/")[4];

	// Setting states of the profile.
	const [editable, setEditable] = useState([])
	const [connectable, setConnectable] = useState([])
	
	// Data soon to be fetched from
	const [profile, setProfile] = useState(null)
	const [connections, setConnections] = useState([])
	const [badges, setBadges] = useState(null)

	// A key mapping to show which tasks of which project to be displayed.
	const [project_taskNo, setProjectTaskNo] = useState({})

	const fetchProfile = async () => {
		// Fetching the profile
		const response1 = await fetch("http://localhost:8000/profile?" + new URLSearchParams({"token" : token, "username" : username}).toString());
		if (response1.ok) {
			const profile_response = await response1.json();
			// Checking access and setting states
			if (profile_response.access === "self") {
				setEditable(true);
				setConnectable(false);
				setProfile(profile_response.user_details)
			} else if (profile_response.access === "connected") {
				console.log(profile_response)
				setEditable(false);
				setConnectable(false);
				setProfile(profile_response.user_details)
			} else {
				setEditable(false);
				setConnectable(true);
				setProfile(profile_response.user_details)
			}
		} else {
			window.location.href = "http://localhost:3000";
		}

		// Fetching connections of this user.
		const response2 = await fetch("http://localhost:8000/connections?" + new URLSearchParams({"token" : token, "username" : username}).toString())
		if (response2.ok) {
			const connections_response = await response2.json();
			setConnections(connections_response)
		}

		// Fetching badges of this user.
		const response3 = await fetch(`http://localhost:8000/users/${username}/badges?` + new URLSearchParams({"username" : username, "token" : token}).toString());
		if (response3.ok) {
			const badge_response = await response3.json();
			console.log(badge_response);
			setBadges(badge_response)
			if (badge_response === null) {
				document.getElementById("message").innerHTML = "No badges...yet"
			}
		} else  {
			console.log(response3);
		}
	}
	
	useEffect(() => {
		fetchProfile();
	}, []);

	// If a user desired to connect with the profile, a request is sent to the backend.
	const handleConnectClicked = (event) => {
		fetch("http://localhost:8000/connections/requests", {
			method: "POST",
			headers: { "Content-Type" : "application/json" },
			body : JSON.stringify({"sender_token" : token, "receiver_username" : username})
		}).then((response) => {
			if (response.ok) {
					document.getElementById("message").innerHTML = "Connect Request Sent."
			}
		})
	}

	function setNewTaskNo(id) {
		project_taskNo[id] = 0;
		setProjectTaskNo(project_taskNo);
	}

	const antImageMap = {
		"black" : ant_black,
		"blue" : ant_blue,
		"green" : ant_green,
		"purple" : ant_purple,
		"red" : ant_red,
		"yellow" : ant_yellow
	}

	const badgeImageMap = {
		"CHAD 1": CHAD_1,
		"CHAD 2": CHAD_2,
		"CHAD 3": CHAD_3
	}

	// Variable saving the previously picked colour of the ant.
	var prevColour = "";

	// When the user clicks a certain ant.
	function clickedAnt(colour) {
		if (prevColour.length > 0) {
			// The previously selected ant's border goes back to normal
			document.getElementById(`ant_${prevColour}`).style.border = "initial"
		}
		
		// The currently picked ant's border is bolded
		document.getElementById(`ant_${colour}`).style.border = "medium solid"
		
		// The big profile image is changed to this picked colour
		document.getElementById("antProfile").src = antImageMap[colour];
		
		// The picked colour is saved as the previous before the function is finished.
		prevColour = colour;
	}

	const colours = ["black", "blue", "green", "purple", "red", "yellow"]

	// When user submits a change the image source saved in the frontend storage is modified.
	const antColourChanged = (event) => {
		if (localStorage.getItem("userAntColours") == null) {
			localStorage.setItem("userAntColours", JSON.stringify({[sessionStorage.getItem("username")]: [document.getElementById("antProfile").src]}))
		} else {
			const newData = JSON.parse(localStorage.getItem("userAntColours"))
			newData[sessionStorage.getItem("username")] = document.getElementById("antProfile").src;
			localStorage.setItem("userAntColours", JSON.stringify(newData))
			console.log(localStorage.getItem("userAntColours"))
		}
	}

	// Finds the image source of the username's picked ant. If they have not picked yet, we return the normal black ant.
	function findAntImageSrc(username) {
		if (localStorage.getItem("userAntColours") == null) {
			return ant_black
		}
		if (JSON.parse(localStorage.getItem("userAntColours"))[username] === undefined) {
			return ant_black
		}
		return JSON.parse(localStorage.getItem("userAntColours"))[username];
	}

	function handleProjectClicked(project_id) {
		window.location.href = `http://localhost:3000/project/${project_id}`;
	}

	return (
		<ChakraProvider theme={theme}>
			<NavBar />
			<Box textAlign="center" fontSize="xl">
				<Grid minH="80vh" p={3}>
					<ColorModeSwitcher justifySelf="flex-end" />
					<VStack spacing={5}>
						<Text fontSize="4xl">Profile</Text>
						<HStack spacing="50px">
							<VStack spacing="20px">
								<Image id="antProfile" boxSize="256px" src={findAntImageSrc(username)}/>
								<Popover boxSize="500px">
									<PopoverTrigger>
										<Button hidden={editable ? false : true}>Choose Ant</Button>
									</PopoverTrigger>
									<PopoverContent width="450px">
										<PopoverCloseButton />
										<PopoverHeader>Choose your ant colour</PopoverHeader>
										<PopoverBody>
											<VStack>
												<HStack>
													{colours.map((colour) => (
														<Image id={`ant_${colour}`} boxSize="64px" src={antImageMap[colour]} onClick={() => clickedAnt(colour)}></Image>
													))}
												</HStack>
												<Divider/>
												<Button onClick={antColourChanged}>Change</Button>
											</VStack>
										</PopoverBody>
									</PopoverContent>
								</Popover>
							</VStack>
							<Stack textAlign="start">
								<Text>Name - {profile && profile.firstname} {profile && profile.lastname}</Text>
								<Text>Username - {profile && profile.username}</Text>
								<Text>Email - {profile && profile.email}</Text>
							</Stack>
						</HStack>

						<Stack>
							<Text fontSize='3xl'>Badges</Text>
							{badges && badges.length == 0 ? <Text>No Badges yet...</Text> : 
							<HStack>
								<Text id = "badgeMessage"></Text>
								{badges && badges.map((badge) => (
									<Image id={`${badge.name}`} boxSize="64px" src={badgeImageMap[badge.name]}></Image>
								))}
							</HStack>
							}
						</Stack>
						<Button hidden={connectable ? false : true} onClick={handleConnectClicked}>Connect</Button>
						<Text id="message"></Text>
						<Stack hidden={connectable ? true : false}>
							<Text fontSize='3xl'>Projects</Text>
							{console.log(profile)}
							{<Stack>
								{profile && profile.projects.map((project) => (
									<HStack key={project.id} borderWidth="1px" padding="10px">
										<script>{!(project.id in project_taskNo) && setNewTaskNo(project.id)}</script>
										<Button onClick={() => handleProjectClicked(project.id)} fontSize="2xl">{project.title}</Button>
										<Divider orientation="vertical"/>
										<Text>Assigned Tasks</Text>
										<IconButton isDisabled={project_taskNo[project.id] === 0} onClick={() => setProjectTaskNo({...project_taskNo, [project.id] : project_taskNo[project.id] - 1})} icon={<ArrowLeftIcon/>}></IconButton>
										<Text>{project.tasks.length > project_taskNo[project.id] && project.tasks[project_taskNo[project.id]].title}</Text>
										<IconButton isDisabled={project.tasks.length <= project_taskNo[project.id] + 1} onClick={() => setProjectTaskNo({...project_taskNo, [project.id] : project_taskNo[project.id] + 1})} icon={<ArrowRightIcon/>}></IconButton>
									</HStack>
								))}
							</Stack>}
						</Stack>
						<Text hidden={connectable}>Connections</Text>
						<HStack hidden={connectable}>
							{connections && connections.map((connection) => (
								<HStack borderWidth="1px" padding="10px" spacing="20px" _hover={{textDecoration: "underline"}} cursor="pointer" onClick={() => window.location.href=`http://localhost:3000/profile/${connection.username}`}>
									<Avatar src={findAntImageSrc(connection.username)}></Avatar>
									<Stack>
										<Text>{connection.firstname} {connection.lastname}</Text>
										<Text>@{connection.username}</Text>
									</Stack>
								</HStack>
							))}
						</HStack>
					</VStack>
				</Grid>
			</Box>
		</ChakraProvider>
	);
}