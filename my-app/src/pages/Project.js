import {
	AddIcon,
	CheckIcon,
	ChevronDownIcon, 
	CloseIcon, 
	EditIcon
} from '@chakra-ui/icons';
import {
	Avatar,
	Box,
	Button,
	ButtonGroup,
	ChakraProvider,
	Divider,
	Drawer,
	DrawerBody,
	DrawerCloseButton,
	DrawerContent,
	DrawerFooter,
	DrawerHeader,
	DrawerOverlay,
	Editable,
	EditableInput,
	EditablePreview,
	Flex,
	FormControl,
	FormLabel,
	Grid,
	HStack,
	IconButton,
	Input,
	InputGroup,
	InputLeftAddon,
	Menu,
	MenuButton,
	MenuItem,
	MenuList,
	NumberIncrementStepper,
	NumberDecrementStepper,
	NumberInput,
	NumberInputField,
	NumberInputStepper,
	Select,
	Spacer,
	Stack,
	Text,
	theme,
	Tooltip,
	useDisclosure,
	useEditableControls,
	VStack
} from '@chakra-ui/react';
import React, { useEffect, useState, useRef} from "react";

import { ColorModeSwitcher } from './../components/ColorModeSwitcher';
import { NavBar } from "../components/NavBar";

import ant_black from "./../images/ant_black.png";

// Context provider for projects
const ProjectContext = React.createContext({
	project: {}, fetchProject: () => {},
	addable_users: [], fetchAddableUsers: () => [],
	tasks: [], fetchTasks: () => []
})

export default function Project() {
	// If the token does not exist, users are redirected to the home page.
	if (!JSON.parse(sessionStorage.getItem("token"))) {
		window.location.href = "http://localhost:3000";
	}	
	const token = JSON.parse(sessionStorage.getItem("token")).access_token;
	
	// The project id is retrieved from the URL
	const p_id = window.location.href.split("/")[4];
	
	const [project, setProject] = useState(null);
	const [addable_users, setAddableUsers] = useState(null);
	const [tasks, setTasks] = useState(null);

	const fetchProject = async () => {
		const response = await fetch("http://localhost:8000/project?" + new URLSearchParams({"token" : token, "p_id" : p_id}).toString());
		if (response.ok) {
			const project_response = await response.json();
			setProject(project_response)
		} else {
			window.location.href = "http://localhost:3000";
		}
	}

	const fetchAddableUsers = async () => {
		const response = await fetch(`http://localhost:8000/project/${p_id}/users/addable?` + new URLSearchParams({"project_id" : p_id, "token" : token}).toString());
		if (response.ok) {
			const addable_users_response = await response.json();
			setAddableUsers(addable_users_response)
		}
}

	const fetchTasks = async () => {
		const response = await fetch(`http://localhost:8000/project/${p_id}/tasks?` + new URLSearchParams({"project_id" : p_id, "token" : token}).toString());
		if (response.ok) {
			const tasks_response = await response.json();
			setTasks(tasks_response);
		}
	}

	useEffect(() => {
		fetchProject();
		fetchAddableUsers();
		fetchTasks();
	}, [])

	// When the user clicked the Add User button, we show a list of connected users that can be added to the project.
	const handleAddUserClicked = (event) => {
		if (addable_users.length === 0) {
			document.getElementById("message").innerHTML = "No users to add."
		} else {
			document.getElementById("addable_users").hidden = false;
		}
	}

	// When the user clicks the user to be added to the project, it posts the data to the backend and reloads the page.
	async function handleUserClicked(user_id) {
		await fetch (`http://localhost:8000/project/${p_id}/users/add`, {
			method: "PUT",
			headers: 
			{
				"Content-Type" : "application/json",
				"Access-Control-Allow-Origin":  'http://localhost:3000'
			},
			body : JSON.stringify({
				"project_id" : p_id,
				"user_id": user_id,
				"token" : token
			})
		}).then((response) => {
			if (response.ok) {
				document.getElementById("message").innerHTML = "Added.";
				window.location.reload()
			}
		})
	}

	// When the user wants to add a new task, the data is posted to the backend and the page is reloaded.
	const handleAddClicked = async (event) => {
		await fetch(`http://localhost:8000/project/${p_id}/newtask`, {
			method: "POST",
			headers: {"Content-Type" : "application/json"},
			body: JSON.stringify({
				"token" : token,
				"project_id" : p_id,
				"taskInfo" : {
					"title" : document.getElementById("title").value,
					"description" : document.getElementById("description").value,
					"reward" : document.getElementById("reward").value,
					"deadline" : document.getElementById("deadline").value,
					"assignee" : document.getElementById("assignee").value
				}
			})
		}).then((response) => {
			if (response.ok) {
				document.getElementById("message").innerHTML = "Added.";
				window.location.reload()
			}
		})
	}

	// Edits to the tasks are posted to the backend.
	async function handleTaskChanged(t_id) {
		if (t_id != 0 && taskIsChanged()) {
			await fetch (`http://localhost:8000/project/${p_id}/${t_id}`, {
				method: "PUT",
				headers: {
					"Content-Type" : "application/json",
					"Access-Control-Allow-Origin":  'http://localhost:3000'
				},
				body : JSON.stringify({
					"project_id" : p_id,
					"task_id": t_id,
					"token" : token,
					"taskInfo" : {
						"title" : title,
						"dscrptn" : description,
						"assignee" : assignee,
						"reward" : reward,
						"status" : findTaskStateInt(status),
						"deadline" : dueDate,
						"importance" : findImportanceInt(importance)
					}
				})
			})
		}
	}

	// Translates the string of Task State to the Enum number.
	function findTaskStateInt(str) {
		if (str === "Not Started") { return 1; }
		if (str === "In Progress") { return 2; }
		if (str === "Blocked") { return 3; }
		return 4;
	}

	// Translates the string of Importance to the Enum number.
	function findImportanceInt(str) {
		if (str === "Low") { return 1; }
		if (str === "Normal") { return 2; }
		if (str === "High") { return 3; }
		return 4;
	}

	// Controls for the Title and Description input
	function EditableControls() {
		const {
		isEditing,
		getSubmitButtonProps,
		getCancelButtonProps,
		getEditButtonProps,
		} = useEditableControls()

		return isEditing ? (
		<ButtonGroup size='sm'>
			<IconButton icon={<CheckIcon />} {...getSubmitButtonProps()} s/>
			<IconButton icon={<CloseIcon />} {...getCancelButtonProps()} />
		</ButtonGroup>
		) : (
		<Flex>
			<IconButton size='sm' icon={<EditIcon />} {...getEditButtonProps()} />
		</Flex>
		)
  	}	

	const { isOpen, onOpen, onClose } = useDisclosure()
 	const btnRef = React.useRef()

	// When only the status is changed, the change is posted to the backend.
	async function handleStatusChanged(task) {
		const status_int = findTaskStateInt(document.getElementById(`${task.id}_quickEditStatus`).value);
		await fetch (`http://localhost:8000/project/${p_id}/${task.id}`, {
			method: "PUT",
			headers: {"Content-Type" : "application/json"},
			body : JSON.stringify({
				"project_id" : p_id,
				"task_id": task.id,
				"token" : token,
				"taskInfo" : {
					"assignee" : task.assignee,
					"reward" : task.reward,
					"status" : status_int,
					"title" : task.title
				}
			})
		})
		setStatus(status_int)
		console.log(status)
	}

	// When only the assignee is changed, the change is posted to the backend.
	async function handleAssigneeChanged(task, user_id) {
		await fetch (`http://localhost:8000/project/${p_id}/${task.id}`, {
			method: "PUT",
			headers: {"Content-Type" : "application/json"},
			body : JSON.stringify({
				"project_id" : p_id,
				"task_id": task.id,
				"token" : token,
				"taskInfo" : {
					"assignee" : user_id,
					"reward" : task.reward,
					"title" : task.title
				}
			})
		}).then((response) => {
			if (response.ok) {
				window.location.reload()
			}
		})
	}

	// When the edit button is clicked, the task data is saved to be shown on the drawer.
	function handleEditClicked(task) {
		setDrawerTask(task)
		setTitle(task.title)
		setDescription(task.description)
		setAssignee(task.assignee)
		setReward(task.reward)
		console.log(document.getElementById(`${task.id}_quickEditStatus`).value)
		setStatus(document.getElementById(`${task.id}_quickEditStatus`).value)
		setDueDate(task.due_date)
		setImportance(task.importance)
		setID(task.id)
		setLabels(task.labels)
		onOpen()
	}

	const [drawerTask, setDrawerTask] = useState({})
	const [title, setTitle] = useState("")
	const [description, setDescription] = useState("")
	const [assignee, setAssignee] = useState(0)
	const [reward, setReward] = useState(0)
	const [status, setStatus] = useState(0)
	const [dueDate, setDueDate] = useState(null)
	const [importance, setImportance] = useState(0)
	const [id, setID] = useState(0)
	const [labels, setLabels] = useState([])
	const [labelTitle, setLabelTitle] = useState("")


	// Listens to input changes and saves it
	const handleTitleInput = event => {
		setTitle(event.target.value)
	}
	const handleDescriptionInput = event => {
		setDescription(event.target.value)
	}
	const handleAssigneeInput = event => {
		console.log(event.target.value)
		setAssignee(event.target.value)
	}
	const handleRewardInput = value => {
		setReward(value)
	}
	const handleStatusInput = event => {
		setStatus(event.target.value)
	}
	const handleDueDateInput = event => {
		setDueDate(event.target.value)
	}
	const handleImportanceInput = event => {
		setImportance(event.target.value)
	}
	const handleLabelInput = event => {
		setLabelTitle(event.target.value)
	}
	
	// Detection to changes in the values in the list handles the task change being posted to the backend.
	useEffect(() => {
		handleTaskChanged(id)
	}, [assignee, status, importance, reward, dueDate])

	const [isEditingLabel, setIsEditingLabel] = useState(false);
  	const [labelText, setLabelText] = useState('');

	async function handleAddLabel(label) {
		// Add label to the task or project
		await fetch (`http://localhost:8000/project/${p_id}/${id}/labels`, {
			method: "POST",
			headers: {"Content-Type" : "application/json"},
			body : JSON.stringify({
				token : token,
				project_id : p_id,
				task_id: id,
				label_title: label
			})
		}).then((response) => {
			if (response.ok) {
				window.location.reload()
			}
		})
		setIsEditingLabel(false);
		setLabelText('');
	}

	async function handleLabelChanged(label_id, label_title) {
		console.log(label_id)
		console.log(label_title)
		await fetch (`http://localhost:8000/project/${p_id}/${id}/labels/update`, {
			method: "POST",
			headers: {"Content-Type" : "application/json"},
			body : JSON.stringify({
				"token" : token,
				"label_id": label_id,
				"label_title": label_title
			})
		}).then((response) => {
			if (response.ok) {
				window.location.reload()
			}
		})
		
	}

	const handleDrawerClosed = () => {
		onClose()
		if (taskIsChanged()) {
			window.location.reload()
		}
	}

	// Checks if the task data has been changed from the initial drawer task status.
	function taskIsChanged() {
		return (
			!(drawerTask.title === title) ||
			!(drawerTask.description === description) ||
			!(drawerTask.assignee === assignee) ||
			!(drawerTask.reward === reward) ||
			!(drawerTask.status === findTaskStateInt(status)-1) ||
			!(drawerTask.due_date === dueDate) ||
			!(drawerTask.importance === importance)
		);
	}

	// When the avatar at the top is clicked, tasks are filtered.
	function handleAvatarClicked(username) {
		// If the user was previously selected, they take them out of the selected users list.
		if (currentUserSelection.includes(username)) {
			document.getElementById(`avatar_${username}`).style.border = "initial"
			setCurrentUserSelection(currentUserSelection.filter(existingUsername => existingUsername !== username))
		} 
		
		// If the user has not been selected, we put them into the selected users list.
		else {
			document.getElementById(`avatar_${username}`).style.border = "medium solid grey";
			setCurrentUserSelection(currentUserSelection => [... currentUserSelection, username])
		}
	}

	// State that saves the users that's currently selected to show assigned tasks.
	const [currentUserSelection, setCurrentUserSelection] = useState([])

	const userAntColours = JSON.parse(localStorage.getItem("userAntColours"));
	function findAntImageSrc(username) {
		if (localStorage.getItem("userAntColours") == null) { 
			return ant_black
		} else if (userAntColours[username] === null) {
			return ant_black
		}
		return userAntColours[username];
	}

	

	return (
		<ProjectContext.Provider>
			<ChakraProvider theme={theme}>
				<NavBar />
				
				<Box textAlign="center" fontSize="xl">
					<Grid minH="100vh" p={3}>
						<ColorModeSwitcher justifySelf="flex-end" />
						<VStack spacing={8}>
							<Text fontSize="2xl">{project && project.title}</Text>
							
							<HStack>
								{project && project.users.map((user) => (
									<Tooltip label={user.username}>
										<Avatar id={`avatar_${user.username}`} onClick={() => handleAvatarClicked(user.username)} src={findAntImageSrc(user.username)}></Avatar>
									</Tooltip>
								))}
								<Button onClick={handleAddUserClicked}>Add User</Button>
							</HStack>
							<Stack id="addable_users" hidden>
								{addable_users && addable_users.map((user) => (
									<Button onClick={() => handleUserClicked(user.id)}>{user.username}</Button>
								))}
							</Stack>
							<Text id="message"></Text>
							<Text>Tasks</Text>
							<Stack id="tasks">
								{tasks && tasks.map((task) => (
									<Box textAlign="start" borderWidth="1px" padding="10px" id={`task_${task.id}`} hidden={currentUserSelection.length > 0 && !currentUserSelection.includes(task.assigned_user.username)}>
										<HStack>
											<Text fontSize='2xl'>{task.title}</Text>
											<Divider orientation="vertical"/>
											<Text>{task.description}</Text>
											<Spacer />
											<Select id={`${task.id}_quickEditStatus`} onChange={() => handleStatusChanged(task)} width="150px">
												<option selected={task.status === 0}>Not Started</option>
												<option selected={task.status === 1}>In Progress</option>
												<option selected={task.status === 2}>Blocked</option>
												<option selected={task.status === 3}>Completed</option>
											</Select>
											<Text>Due: {task.due_date}</Text>
											<Menu>
												<Tooltip id="test" label={`Assignee: ${task.assignee}`}>
													<MenuButton>
														{userAntColours && userAntColours[task.assignee] ? (
														<Avatar
															id={`avatar_${task.assignee}`}
															src={userAntColours[task.assignee]}
														></Avatar>
														) : (
														<Avatar
															id={`avatar_${task.assignee}`}
															src={findAntImageSrc(task.assigned_user.username)}
														></Avatar>
														)}		
														<Text>{task.assigned_user.username}</Text>
													</MenuButton>
												</Tooltip>
												<MenuList padding="10px" width="auto">
													{project && project.users.map((user) => (
														<MenuItem onClick={() => handleAssigneeChanged(task, user.id)}>
															<HStack>
															{userAntColours && userAntColours[user.username] ? (
																<Avatar
																	id={`avatar_${user.username}`}
																	src={userAntColours[user.username]}
																></Avatar>
																) : (
																<Avatar
																	id={`avatar_${user.username}`}
																	src={ant_black}
																></Avatar>
															)}
															<Text>{user.username}</Text>
															</HStack>
														</MenuItem>
													))}
												</MenuList>
											</Menu>
											<>
												<IconButton icon={<EditIcon/>} onClick={() => handleEditClicked(task)}></IconButton>
												<Drawer isOpen={isOpen} placement="right" onClose={handleDrawerClosed} finalFocusRef={btnRef}>
													<DrawerOverlay />
													<DrawerContent>
														<DrawerCloseButton />
														<DrawerHeader>Task Information</DrawerHeader>
														<DrawerBody>
															<Stack>
																<Editable
																	defaultValue={title}
																	fontSize='2xl'
																	isPreviewFocusable={false}
																	onSubmit={() => handleTaskChanged(id)}
																>
																	<HStack>
																		<EditablePreview />
																		{/* Here is the custom input */}
																		<Input as={EditableInput} onChange={handleTitleInput}/>
																		<EditableControls />
																	</HStack>
																</Editable>

																<Editable
																	defaultValue={description}
																	isPreviewFocusable={false}
																	onSubmit={() => handleTaskChanged(id)}
																>
																	<HStack>
																		<EditablePreview />
																		{/* Here is the custom input */}
																		<Input as={EditableInput} onChange={handleDescriptionInput}/>
																		<EditableControls />
																	</HStack>
																</Editable>
																<Text>Assigned to:</Text>
																<Select onChange={handleAssigneeInput} defaultValue={assignee}>
																{project && project.users.map((user) => (
																	<option value={user.id}>{user.username}</option>
																))}
															</Select>
																<Text>Reward:</Text>
																<NumberInput onChange={handleRewardInput} defaultValue={reward} min={1}>
																	<NumberInputField/>
																	<NumberInputStepper>
																		<NumberIncrementStepper />
																		<NumberDecrementStepper />
																	</NumberInputStepper>
																</NumberInput>
																<Text>Status:</Text>
																<Select onChange={handleStatusInput} defaultValue={status}>
																	<option >Not Started</option>
																	<option >In Progress</option>
																	<option >Blocked</option>
																	<option >Completed</option>
																</Select>
																<Text>Due Date:</Text>
																<Input
																	defaultValue={dueDate}
																	size="md"
																	type="date"
																	onChange={handleDueDateInput}
																/>
																<Text>Importance:</Text>
																<Select onChange={handleImportanceInput}>
																	<option selected={importance === 0}>Low</option>
																	<option selected={importance === 1}>Normal</option>
																	<option selected={importance === 2}>High</option>
																	<option selected={importance === 3}>Very High</option>
																</Select>
																<Text>Labels:</Text>
																{labels.map((label) => (
																	<Editable
																		key={label.id}
																		defaultValue={label.title}
																		fontSize='2xl'
																		isPreviewFocusable={false}
																		onSubmit={() => handleLabelChanged(label.id, labelTitle)}
																  	>
																	<HStack>
																		<EditablePreview />
																		{/* Here is the custom input */}
																		<Input as={EditableInput} onChange={handleLabelInput}/>
																		<EditableControls />
																	</HStack>
																	</Editable>
																))}
																{isEditingLabel ? (
																	<form onSubmit={(event) => event.preventDefault()}>
																	<Input
																	type="text"
																	value={labelText}
																	onChange={(event) => setLabelText(event.target.value)}
																	/>
																	<Button onClick={() => handleAddLabel(labelText)}>Submit</Button>	
																	</form>
																) : (
																	<Button onClick={() => setIsEditingLabel(true)}>Add Label</Button>
																)}
															</Stack>
														</DrawerBody>
													</DrawerContent>
												</Drawer>
											</>
										</HStack>
									</Box>
								))}
							</Stack>
							<Button onClick={() => document.getElementById("form").hidden = false}>Add Task</Button>
							<form id="form" hidden>
								<Text>New Task</Text>
								<InputGroup>
									<InputLeftAddon children="Title" />
									<Input
										pr="4.5rem"
										type="text"
										id="title"
									/>
								</InputGroup>
								<InputGroup>
									<InputLeftAddon children="Description" />
									<Input
										pr="4.5rem"
										type="text"
										id="description"
									/>
								</InputGroup>
								<InputGroup>
									<InputLeftAddon children="Assignee" />
									<Select id="assignee" defaultValue="hehe">
										{project && project.users.map((user) => (
											<option defaultValue>{user.username}</option>
										))}
									</Select>
								</InputGroup>
								<InputGroup>
									<InputLeftAddon children="Reward" />
									<Input
										pr="4.5rem"
										type="number"
										id="reward"
									/>
								</InputGroup>
								<InputGroup>
									<InputLeftAddon children="Deadline" />
									<Input
										pr="4.5rem"
										type="date"
										id="deadline"
									/>
								</InputGroup>
								<Button onClick={handleAddClicked}>Add</Button>
							</form>
						</VStack>
					</Grid>
				</Box>
			</ChakraProvider>
		</ProjectContext.Provider>
	)
}