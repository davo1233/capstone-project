import {
    Box,
    Button,
    ChakraProvider,
    Grid,
    Stack,
    Text,
    theme,
    VStack
} from "@chakra-ui/react";
import React, { useEffect, useState } from "react";

import { ColorModeSwitcher } from "../components/ColorModeSwitcher";
import { NavBar } from "../components/NavBar";

// Context provider that saves the results.
const ResultsContext = React.createContext({
    results : [], fetchResults: () => {}
})

export default function UserSearch() {
    // If the token is not found, user is redirected to the home page.
    if (!JSON.parse(sessionStorage.getItem("token"))) {
		window.location.href = "http://localhost:3000";
	}
    const token = JSON.parse(sessionStorage.getItem("token")).access_token;

    // The query is retrieved from the URL
    const query = window.location.href.split("/")[4];

    const [results, setResults] = useState([]); 

    const fetchResults = async () => {
        const response = await fetch("http://localhost:8000/search?" + new URLSearchParams({"token" : token, "query" : query}).toString());
        if (response.ok) {
            const results_response = await response.json();
            console.log(results_response);
            setResults(results_response);
        }
    }

    useEffect(() => {
        fetchResults();
    }, [])

    // When the username is clicked the user is redirected to the profile of that user.
    function handleUsernameClicked(username) {
        window.location.href = `http://localhost:3000/profile/${username}`;
    }

    return (
        <ResultsContext.Provider value={{results, fetchResults}}>
            <ChakraProvider theme={theme}>
                <NavBar />
				<Box textAlign="center" fontSize="xl">
					<Grid minH="100vh" p={3}>
						<ColorModeSwitcher justifySelf="flex-end" />
						<VStack spacing={8}>
							<Text>Search Results</Text>
                            <Stack spacing={5}>
                                {results.map((user) => (
                                    <Button onClick={() => handleUsernameClicked(user.username)}>{user.username}</Button>
                                ))}
                            </Stack>
						</VStack>
					</Grid>
				</Box>
			</ChakraProvider>
        </ResultsContext.Provider>
        
    )
}