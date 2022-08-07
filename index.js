
const dotenv = require('dotenv').config();
const { Client } = require('@notionhq/client');

//intialize notion client
const notion = new Client({
    auth: process.env.NOTION_TOKEN,
    // Notion-Version: '2021-08-16'
});

const database_id = process.env.NOTION_DATABASE_ID;

// const listDatabases = async () => {
//     const databaseId = process.env.NOTION_DATABASE_ID;
//     const response = await notion.databases.query({
//         database_id: databaseId,
//         properties:{
//             Tags:{
//                 multi_select: {
//                     options:{
//                         name: "Daily"
//                     },
//                 },
//             },
//         },
// })};
// listDatabases();


// (async () => {
//     const databaseId = database_id;
//     const response = await notion.databases.retrieve({ database_id: databaseId });
//     console.log(response);
//   })();

const querydb = async () => {
    const databaseId = database_id;
    const response = await notion.databases.query({
        database_id: databaseId,
        properties:{
            Tags:{
                multi_select: {
                    options:{
                        name: "Daily"
                    },
                },
            },
        },
    })
    // console.log(response);
    response.options
    // console.log(response.page);
    response.results.forEach(page => {
        console.log(page);
    });
};
querydb();

// (async () => {
//     const blockId = '';
//     const response = await notion.blocks.retrieve({
//       block_id: blockId,
//     });
//     console.log(response);
//     // response.results.forEach(block => {
//     //         console.log(block);
//     // });
//   })();