'use strict';

const fs = require('fs');
const path = require('path');
const helper = require('../src/helper');
const UserInfoManager = require('../src/userInfoManager');

describe('UserInfoManager', () => {
    const testFilePath = './.cache/test_userInfo.json';
    let manager;

    beforeEach(() => {
        manager = new UserInfoManager(testFilePath);
        // Clean up any existing test file
        if (fs.existsSync(testFilePath)) {
            fs.unlinkSync(testFilePath);
        }
    });

    afterEach(() => {
        // Clean up test file
        if (fs.existsSync(testFilePath)) {
            fs.unlinkSync(testFilePath);
        }
    });

    test('should initialize with empty user map', () => {
        expect(manager.getUserMap()).toEqual({});
        expect(manager.nextUid).toBe(30000);
    });

    test('should generate UIDs starting from 30000', () => {
        const uid1 = manager.getUidOrCreate('user1');
        const uid2 = manager.getUidOrCreate('user2');

        expect(uid1).toBe('30000');
        expect(uid2).toBe('30001');
    });

    test('should preserve existing UIDs', () => {
        const uid1 = manager.getUidOrCreate('user1');
        manager.save();

        // Create new instance to test loading
        const newManager = new UserInfoManager(testFilePath);
        newManager.load();

        expect(newManager.getUidOrCreate('user1')).toBe(uid1);
    });

    test('should handle cleanup properly', () => {
        manager.getUidOrCreate('user1');
        manager.getUidOrCreate('user2');
        
        manager.cleanup();
        
        expect(manager.getUserMap()).toEqual({});
        expect(manager.nextUid).toBe(30000);
    });

    test('should save and load user mappings', () => {
        const testUsers = {
            'user1': '30000',
            'user2': '30001'
        };

        // Create mappings
        Object.keys(testUsers).forEach(username => {
            manager.getUidOrCreate(username);
        });

        // Save to file
        const saveResult = manager.save();
        expect(saveResult).toBe(true);

        // Load in new instance
        const newManager = new UserInfoManager(testFilePath);
        newManager.load();

        expect(newManager.getUserMap()).toEqual(testUsers);
    });
});
