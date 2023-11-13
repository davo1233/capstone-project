import {
    Menu,
    MenuButton,
    MenuList,
	Button,
	MenuDivider,
	MenuOptionGroup,
	MenuItemOption,
	InputGroup,
	Input,
	InputRightElement,
	HStack,
	VStack
  } from '@chakra-ui/react';

import {useState} from 'react';

const TaskFilter = ({project_id}) => {
    const[lookup,setLookup] = useState('');
	const [filterType, setFilterType] = useState('1');
	const token = JSON.parse(sessionStorage.getItem("token")).access_token;
    const handleChangeTasksFilter = async (event) => {
		event.preventDefault();
        const response = await fetch("http://localhost:8000/project" + new URLSearchParams({"project_id": project_id,"token" : token, "filter_type" : parseInt(filterType), "lookup": parseInt(lookup)}).toString());
		if (response.ok) {
			const sort_tasks_response = await response.json();
		} else {
			console.log('fail')
		}
    }

    return (
		<Menu closeOnSelect={false} spacing = {8}>
		
		<HStack>
			<VStack>
				<MenuButton as={Button} colorScheme='blue'>
				Task Filter Settings
				</MenuButton>
			</VStack>
			<MenuList minWidth='240px'>
			<MenuDivider />
				<MenuOptionGroup 
					title='Filter Type' 
					defaultValue ='1' type='radio' 
					onChange={(value) => setFilterType(value)}
				>
					<MenuItemOption value='1'>Time created</MenuItemOption>
					<MenuItemOption value='2'>Deadline</MenuItemOption>
					<MenuItemOption value='3'>Assignee</MenuItemOption>
				</MenuOptionGroup>
			</MenuList>
		</HStack>
		<VStack>
		<InputGroup size='md'>
            <Input
                pr="4.5rem"
                type="text"
                placeholder='Filter tasks...'
                onChange = {(e) => setLookup(e.target.value)}
            />
            <InputRightElement width='4.5rem'>
                <Button h='1.75rem' size='sm' onClick={handleChangeTasksFilter}>
                    Search
                </Button>
            </InputRightElement>
        </InputGroup>
		</VStack>
        
	  </Menu>


    );
};

export default TaskFilter;