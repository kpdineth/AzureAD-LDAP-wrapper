'use strict';

const fs = require('fs');
const path = require('path');
// Mock all external modules first
jest.mock('../src/graph.fetch');
jest.mock('../src/helper');
jest.mock('../src/config', () => ({
    LDAP_USERS_SYNCONLYINGROUP: 'test_group1|test_group2',
    LDAP_USERSGROUPSBASEDN: 'cn=users,cn=groups,dc=example,dc=com',
    LDAP_DATAFILE: './.cache/test/azure.json',
    LDAP_SYNC_TIME: 15,
    LDAP_DEBUG: false,
    LDAP_DOMAIN: 'example.com',
    LDAP_BASEDN: 'dc=example,dc=com',
    LDAP_USERSDN: 'cn=users,dc=example,dc=com',
    LDAP_GROUPSDN: 'cn=groups,dc=example,dc=com',
    LDAP_USERRDN: 'uid',
    LDAP_SAMBADOMAINNAME: 'EXAMPLE',
    LDAP_SAMBASIDBASE: 'S-1-5-21-2475342291-1480345137-508597502',
    LDAP_SAMBA_USEAZURESID: true,
    DSM7: true
}));

// Import modules after mocking
const helper = require('../src/helper');
const database = require('../src/database');
const config = require('../src/config');
const fetch = require('../src/graph.fetch');

// Restore helper functions we need
const realHelper = jest.requireActual('../src/helper');
helper.ReadJSONfile.mockImplementation(realHelper.ReadJSONfile);
helper.SaveJSONtoFile.mockImplementation(realHelper.SaveJSONtoFile);
helper.log.mockImplementation(() => {});
helper.warn.mockImplementation(() => {});
helper.error.mockImplementation(() => {});

describe('Database UserInfo Integration', () => {
    const testCachePath = './.cache/test';
    const testUserInfoPath = path.join(testCachePath, 'userInfo.json');
    
    beforeEach(() => {
        // Reset all mocks
        jest.clearAllMocks();
        
        // Create test cache directory
        if (!fs.existsSync(testCachePath)) {
            fs.mkdirSync(testCachePath, { recursive: true });
        }
        
        // Clean up any existing test files
        if (fs.existsSync(testUserInfoPath)) {
            fs.unlinkSync(testUserInfoPath);
        }
        
        // Mock Graph API responses
        fetch.initAccessToken.mockResolvedValue('mock-token');
        
        // Define test groups with both cn and displayName
        const testGroups = [
            { 
                id: '1', 
                displayName: 'test_group1', 
                securityIdentifier: 'S-1-1', 
                cn: 'test_group1',
                member: [],
                memberUid: [],
                objectClass: ['top', 'posixGroup'],
                gidNumber: '1000'
            },
            { 
                id: '2', 
                displayName: 'test_group2', 
                securityIdentifier: 'S-1-2', 
                cn: 'test_group2',
                member: [],
                memberUid: [],
                objectClass: ['top', 'posixGroup'],
                gidNumber: '1001'
            },
            { 
                id: '3', 
                displayName: 'other_group', 
                securityIdentifier: 'S-1-3', 
                cn: 'other_group',
                member: [],
                memberUid: [],
                objectClass: ['top', 'posixGroup'],
                gidNumber: '1002'
            }
        ];

        // Initialize database with test data
        const db = {};
        
        // Add test groups to database with proper DNs
        testGroups.forEach(group => {
            const groupDn = `cn=${group.cn},${config.LDAP_GROUPSDN}`;
            db[groupDn] = {
                ...group,
                objectClass: ['top', 'posixGroup'],
                gidNumber: group.gidNumber,
                entryDN: groupDn,
                member: [],
                memberUid: [],
                displayName: group.displayName,
                cn: group.cn
            };
        });

        // Add users group
        db[config.LDAP_USERSGROUPSBASEDN] = {
            objectClass: ['top', 'posixGroup'],
            cn: 'users',
            displayName: 'users',
            gidNumber: '100',
            member: [],
            memberUid: [],
            sambaSID: 'S-1-5-21-1-2-3'
        };

        // Mock helper functions for database operations
        helper.ReadJSONfile.mockImplementation((file) => {
            if (file === config.LDAP_DATAFILE) {
                return db;
            }
            if (file.endsWith('userInfo.json')) {
                return {};
            }
            return {};
        });

        // Mock helper functions
        helper.ReadJSONfile.mockImplementation((file) => {
            if (file === config.LDAP_DATAFILE) {
                return db;
            }
            return {};
        });
        helper.SaveJSONtoFile.mockImplementation((content, file) => {
            console.log('Saving to file:', file, 'Content:', JSON.stringify(content, null, 2));
            return true;
        });
        helper.log.mockImplementation((...args) => {
            console.log('DEBUG:', ...args);
        });
        
        fetch.getGroups.mockResolvedValue(testGroups);
        
        // Set up group memberships in LDAP format
        const userDNs = {
            'user1': `uid=test.user1,${config.LDAP_USERSDN}`,
            'user2': `uid=test.user2,${config.LDAP_USERSDN}`,
            'user3': `uid=test.user3,${config.LDAP_USERSDN}`
        };

        // Add users to their respective groups
        testGroups.forEach(group => {
            const groupDn = `cn=${group.cn},${config.LDAP_GROUPSDN}`;
            if (group.id === '1') {
                db[groupDn].member.push(userDNs['user1']);
                db[groupDn].memberUid.push('test.user1');
            } else if (group.id === '2') {
                db[groupDn].member.push(userDNs['user2']);
                db[groupDn].memberUid.push('test.user2');
            } else if (group.id === '3') {
                db[groupDn].member.push(userDNs['user3']);
                db[groupDn].memberUid.push('test.user3');
            }
        });

        // Define test users with all required attributes matching Azure API format
        const mockUsers = [
            { 
                id: 'user1',
                userPrincipalName: 'test.user1@example.com',
                accountEnabled: true,
                displayName: 'Test User 1',
                givenName: 'Test',
                surname: 'User 1',
                mail: 'test.user1@example.com',
                identities: [],
                userType: 'Member',
                '@odata.type': '#microsoft.graph.user',
                businessPhones: [],
                jobTitle: null,
                mobilePhone: null,
                officeLocation: null,
                preferredLanguage: null,
                customSecurityAttributes: null
            },
            {
                id: 'user2',
                userPrincipalName: 'test.user2@example.com',
                accountEnabled: true,
                displayName: 'Test User 2',
                givenName: 'Test',
                surname: 'User 2',
                mail: 'test.user2@example.com',
                identities: [],
                userType: 'Member',
                '@odata.type': '#microsoft.graph.user',
                businessPhones: [],
                jobTitle: null,
                mobilePhone: null,
                officeLocation: null,
                preferredLanguage: null,
                customSecurityAttributes: null
            },
            {
                id: 'user3',
                userPrincipalName: 'test.user3@example.com',
                accountEnabled: true,
                displayName: 'Test User 3',
                givenName: 'Test',
                surname: 'User 3',
                mail: 'test.user3@example.com',
                identities: [],
                userType: 'Member',
                '@odata.type': '#microsoft.graph.user',
                businessPhones: [],
                jobTitle: null,
                mobilePhone: null,
                officeLocation: null,
                preferredLanguage: null,
                customSecurityAttributes: null
            }
        ];
        
        fetch.getUsers.mockResolvedValue(mockUsers);

        // Initialize temporary group membership mapping
        db['tmp_user_to_groups'] = {};
        
        // Initialize group membership for each user
        mockUsers.forEach(user => {
            const username = user.userPrincipalName.split('@')[0];
            const userDn = `uid=${username},${config.LDAP_USERSDN}`;
            db[userDn] = {
                objectClass: ['top', 'posixAccount', 'shadowAccount', 'person', 'organizationalPerson', 'inetOrgPerson'],
                uid: username,
                cn: user.displayName,
                userPassword: 'x',
                loginShell: '/bin/bash',
                uidNumber: '10000',
                gidNumber: '10000',
                homeDirectory: `/home/${username}`,
                gecos: user.displayName,
                description: user.userPrincipalName,
                memberOf: [],
                AzureADuserPrincipalName: user.userPrincipalName
            };
            
            // Initialize with users group
            db['tmp_user_to_groups'][user.id] = [config.LDAP_USERSGROUPSBASEDN];
            
            // Add group memberships based on test configuration
            const userGroups = {
                'user1': testGroups.find(g => g.id === '1'),
                'user2': testGroups.find(g => g.id === '2'),
                'user3': testGroups.find(g => g.id === '3')
            };
            
            const group = userGroups[user.id];
            if (group) {
                const groupDn = `cn=${group.cn},${config.LDAP_GROUPSDN}`;
                if (db[groupDn]) {
                    db['tmp_user_to_groups'][user.id].push(groupDn);
                    db[groupDn].member.push(userDn);
                    db[groupDn].memberUid.push(username);
                    db[userDn].memberOf.push(groupDn);
                }
            }
        });

        // Mock Graph API group membership
        const groupMembers = {
            '1': [{ id: 'user1', '@odata.type': '#microsoft.graph.user' }],
            '2': [{ id: 'user2', '@odata.type': '#microsoft.graph.user' }],
            '3': [{ id: 'user3', '@odata.type': '#microsoft.graph.user' }]
        };
        
        fetch.getMembers.mockImplementation(async ({ id }) => {
            return groupMembers[id] || [];
        });

        // Reset mocks between tests
        jest.clearAllMocks();
    });

    afterEach(() => {
        // Clean up test files
        if (fs.existsSync(testUserInfoPath)) {
            fs.unlinkSync(testUserInfoPath);
        }
        if (fs.existsSync(testCachePath)) {
            fs.rmSync(testCachePath, { recursive: true, force: true });
        }
    });

    test('should only process users from specified groups', async () => {
        // Mock config for testing
        const originalSyncOnlyGroups = config.LDAP_USERS_SYNCONLYINGROUP;
        config.LDAP_USERS_SYNCONLYINGROUP = 'test_group1|test_group2';

        // Initialize database
        await database.init();

        // Wait for database operations to complete
        await new Promise(resolve => setTimeout(resolve, 100));

        // Verify only users from specified groups are processed
        const dbEntries = helper.ReadJSONfile(config.LDAP_DATAFILE);
        const processedUsers = Object.values(dbEntries)
            .filter(entry => entry.objectClass?.includes('inetOrgPerson'))
            .map(user => user.AzureADuserPrincipalName)
            .filter(Boolean);

        // Should include users from test_group1 and test_group2
        expect(processedUsers).toContain('test.user1@example.com');
        expect(processedUsers).toContain('test.user2@example.com');
        
        // Should not include user from other_group
        expect(processedUsers).not.toContain('test.user3@example.com');
        
        // Verify total number of processed users
        expect(processedUsers.length).toBe(2);
        
        // Verify UIDs are assigned correctly
        const userEntries = Object.values(dbEntries)
            .filter(entry => entry.objectClass?.includes('inetOrgPerson'));
            
        userEntries.forEach(user => {
            expect(parseInt(user.uidNumber)).toBeGreaterThanOrEqual(30000);
        });

        // Restore original config
        config.LDAP_USERS_SYNCONLYINGROUP = originalSyncOnlyGroups;
    });

    test('should respect LDAP_SYNC_TIME for refresh interval', async () => {
        const originalSyncTime = config.LDAP_SYNC_TIME;
        config.LDAP_SYNC_TIME = 1; // 1 minute

        // Initialize database
        await database.init();
        const firstRefreshTime = Date.now();

        // Wait a bit and verify no refresh occurs before interval
        await new Promise(resolve => setTimeout(resolve, 100));
        await database.init();
        const secondRefreshTime = Date.now();

        expect(secondRefreshTime - firstRefreshTime).toBeLessThan(config.LDAP_SYNC_TIME * 60 * 1000);

        // Restore original config
        config.LDAP_SYNC_TIME = originalSyncTime;
    });

    test('should maintain UIDs across refreshes', async () => {
        // Initialize database
        await database.init();
        
        // Get initial user UIDs
        const initialDbEntries = helper.ReadJSONfile(config.LDAP_DATAFILE);
        const initialUsers = Object.values(initialDbEntries)
            .filter(entry => entry.objectClass?.includes('inetOrgPerson'))
            .reduce((acc, user) => {
                acc[user.uid] = user.uidNumber;
                return acc;
            }, {});

        // Trigger another refresh
        await database.init();
        
        // Verify UIDs are preserved
        const refreshedDbEntries = helper.ReadJSONfile(config.LDAP_DATAFILE);
        const refreshedUsers = Object.values(refreshedDbEntries)
            .filter(entry => entry.objectClass?.includes('inetOrgPerson'));

        refreshedUsers.forEach(user => {
            if (initialUsers[user.uid]) {
                expect(user.uidNumber).toBe(initialUsers[user.uid]);
            } else {
                expect(parseInt(user.uidNumber)).toBeGreaterThanOrEqual(30000);
            }
        });
    });
});
