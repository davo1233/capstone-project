import {
    Menu,
    MenuButton,
    MenuList,
    MenuItem,
	Button,
	MenuDivider,
	MenuOptionGroup,
	MenuItemOption,
	Box,
	HStack,
	Text,
	Divider,
	Spacer,
	Stack,
	VStack,
  } from '@chakra-ui/react';

import {useState, useEffect } from 'react';

const TaskSort = ({project_id}) => {
	const [ascDesc, setAscDesc] = useState('0');
	const [sortType, setSortType] = useState('0');
	const [tasks, setTasks] = useState([]);
	const token = JSON.parse(sessionStorage.getItem("token")).access_token;
    const handleChangeTasksSort = async (event) => {
		console.log(`sortType ${sortType} asc desc ${ascDesc}`)
        const response = await fetch(`http://localhost:8000/project/${project_id}/tasks/sort/${parseInt(sortType)}/${parseInt(ascDesc)}?` + new URLSearchParams({"token" : token}).toString());
		if (response.ok) {
			const sort_tasks_response = await response.json();
			setTasks(sort_tasks_response);

		} else {
			console.log('did not work');
		}
    }

	useEffect(() => {
		handleChangeTasksSort();
	}, [])

    return (
		<Menu closeOnSelect={false}>
		<MenuButton as={Button} colorScheme='blue'>
		  Task Sort Settings
		</MenuButton>
		<MenuList minWidth='240px'>
		  	<MenuOptionGroup 
				defaultValue='0' 
				title='Order' 
				type='radio'
				onChange={(value) => setAscDesc(value)}
			>
				<MenuItemOption value='0'>Ascending</MenuItemOption>
				<MenuItemOption value='1'>Descending</MenuItemOption>
		  </MenuOptionGroup>
		  <MenuDivider />
		  	<MenuOptionGroup 
				title='Sort Type' 
				defaultValue ='0' type='radio' 
				onChange={(value) => setSortType(value)}
			>
				<MenuItemOption value='0'>Time created</MenuItemOption>
				<MenuItemOption value='1'>Deadline</MenuItemOption>
				<MenuItemOption value='2'>Assignee</MenuItemOption>
		  </MenuOptionGroup>
		</MenuList>
		<Button onClick={handleChangeTasksSort}>Sort</Button>
		<Stack id="tasks">
				{tasks && tasks.map((task) => (
					<VStack>
						<Box textAlign="start" borderWidth="1px" padding="10px" id={`task_${task.id}`} >
							<HStack>
								<Text fontSize='2xl'>{task.title}</Text>
								<Divider orientation="vertical"/>
								<Text>{task.description}</Text>
								<Spacer />
								<Text>Due: {task.due_date}</Text>
							</HStack>
						</Box>
					</VStack>
					
				))}
		</Stack>
	  </Menu>


    );
};

export default TaskSort;