
import {
	Box,
	Button,
	ChakraProvider,
	Grid,
	Input,
	InputGroup,
	InputLeftAddon,
	InputRightElement,
	Stack,
	Text,
	theme,
  	VStack
} from '@chakra-ui/react';
import React, { useEffect, useState } from "react";

import { ColorModeSwitcher } from './../components/ColorModeSwitcher';
import { NavBar } from "../components/NavBar";
import ant_black from "./../images/ant_black.png";
import TaskSort from "../components/TaskSort";
import TaskFilter from "../components/TaskFilter";

// Creating a context that holds project information
const ProjectsContext = React.createContext({
	projects: [], fetchProjects: () => {}
});

export default function Dashboard() {
	// If token cannot be found, user is redirected to the home page.
	if (!JSON.parse(sessionStorage.getItem("token"))) {
		window.location.href = "http://localhost:3000";
	}
	const token = JSON.parse(sessionStorage.getItem("token")).access_token;

	if (localStorage.getItem("userAntColours") == null) {
		localStorage.setItem("userAntColours", JSON.stringify({[sessionStorage.getItem("username")]: ant_black}))
	} 

	const [projects, setProjects] = useState([]);

	const fetchProjects = async () => {
		const response = await fetch("http://localhost:8000/user/projects?" + new URLSearchParams({"token" : token}).toString());

		if (response.ok) {
			const projects_response = await response.json();
			setProjects(projects_response);
		} else {
			// if fetch fails users are redirected to the home page.
			window.location.href = "http://localhost:3000";
		}
		// setProjects([{"id" : 0, "title": "Project 1"}, {"id" : 1, "title": "Project 2"}]);
	};

	useEffect(() => {
		fetchProjects();
	}, []);
	
	// Clicking the project redirects them to the project page.
	function handleProjectClicked(id) {
		window.location.href = `http://localhost:3000/project/${id}`;
	}

	// Clicking the Add Project button shows the form
	const handleAddProjectClicked = (event) => {
		document.getElementById("form").hidden = false;
	};

	// Confirming to create a new project sends a post fetch function to the backend.
	const handleConfirmClicked = async (event) => {
		const response = await fetch("http://localhost:8000/project/create", {
			method: "POST",
			headers: {"Content-Type" : "application/json"},
			body: JSON.stringify({
				"token" : token,
				"title" : document.getElementById("title").value
			})
		});
		const project = await response.json();
		console.log(project)
		
		// After the project creation, user is redirected to the project page of the new project.
		handleProjectClicked(project)
	};

	// When a username is searched, the user is redirected to the search page.
	const handleSearchClicked = (event) => {
		window.location.href = `http://localhost:3000/search/${document.getElementById("searchQuery").value}`;
	};

	return (
		<ProjectsContext.Provider value={{projects, fetchProjects}}>
			<ChakraProvider theme={theme}>
				<NavBar />
				<Box textAlign="center" fontSize="xl">
					<Grid minH="100vh" p={3}>
						<ColorModeSwitcher justifySelf="flex-end" />
						<VStack spacing={8}>
							<Text>Search for users</Text>
							<InputGroup width="300px"> 
								<Input
									type="text"
									placeholder='Search for users...'
									id="searchQuery"
								/>
								<InputRightElement width='4.5rem'>
									<Button h='1.75rem' size='sm' onClick={handleSearchClicked}>
										Search
									</Button>
								</InputRightElement>
							</InputGroup>
							<Stack>
						
							</Stack>
							<Text>Projects</Text>
							<Stack spacing={5}>
							{projects.map((project) => (
								<div key={project.id}>
									<Button onClick={() => handleProjectClicked(project.id)}>{project.title}</Button>
									<div>
										<HStack>
											<TaskSort project_id = {project.id}/>	
										</HStack>
										<HStack>
											<TaskFilter project_id = {project.id}/>
										</HStack>
										
									</div>
								</div>
								))}

							</Stack>
							<Button onClick={handleAddProjectClicked}>Add Project</Button>
							<form id="form" hidden>
								<Stack borderWidth="1px" padding="10px">
									<Text>New Project</Text>
									<InputGroup>
										<InputLeftAddon children="Title" />
										<Input
											pr="4.5rem"
											type="text"
											id="title"
										/>
									</InputGroup>
									<Button onClick={handleConfirmClicked}>Confirm</Button>
								</Stack>
							</form>
						</VStack>
					</Grid>
				</Box>
			</ChakraProvider>
		</ProjectsContext.Provider>
	);
};