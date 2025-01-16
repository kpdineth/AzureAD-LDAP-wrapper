'use strict';

const helper = require('./helper');
const config = require('./config');

/**
 * Manages the userInfo.json file which maintains username to UID mappings
 * @class UserInfoManager
 */
class UserInfoManager {
    /**
     * Creates an instance of UserInfoManager
     * @param {string} [filePath='./.cache/userInfo.json'] - Path to the userInfo.json file
     */
    constructor(filePath = './.cache/userInfo.json') {
        this.filePath = filePath;
        this.userMap = {};
        this.startUid = 30000;
        this.nextUid = this.startUid;
    }

    /**
     * Loads the userInfo.json file from disk
     * @returns {boolean} - Success status of the load operation
     */
    load() {
        try {
            this.userMap = helper.ReadJSONfile(this.filePath);
            
            if (!this.userMap || typeof this.userMap !== 'object') {
                helper.warn("userInfoManager.js", "load()", "Invalid or empty userInfo.json, initializing new map");
                this.userMap = {};
            }

            // Calculate the next available UID
            this.nextUid = Object.values(this.userMap).reduce((maxUid, currentUid) => {
                const uid = parseInt(currentUid, 10);
                return !isNaN(uid) && uid > maxUid ? uid : maxUid;
            }, this.startUid - 1) + 1;

            helper.log("userInfoManager.js", "load()", `Loaded ${Object.keys(this.userMap).length} user mappings, next UID: ${this.nextUid}`);
            return true;
        } catch (error) {
            helper.error("userInfoManager.js", "load()", "Failed to load userInfo.json:", error.message);
            return false;
        }
    }

    /**
     * Saves the current userMap to disk
     * @returns {boolean} - Success status of the save operation
     */
    save() {
        try {
            const success = helper.SaveJSONtoFile(this.userMap, this.filePath);
            if (success) {
                helper.log("userInfoManager.js", "save()", `Saved ${Object.keys(this.userMap).length} user mappings`);
            } else {
                helper.error("userInfoManager.js", "save()", "Failed to save userInfo.json");
            }
            return success;
        } catch (error) {
            helper.error("userInfoManager.js", "save()", "Error saving userInfo.json:", error.message);
            return false;
        }
    }

    /**
     * Gets an existing UID for a username or creates a new one
     * @param {string} username - The username to look up or create a UID for
     * @returns {string} - The UID for the username
     */
    getUidOrCreate(username) {
        if (this.userMap[username] !== undefined) {
            helper.log("userInfoManager.js", "getUidOrCreate()", `Using existing UID ${this.userMap[username]} for user ${username}`);
            return this.userMap[username];
        }

        const newUid = this.nextUid.toString();
        this.userMap[username] = newUid;
        this.nextUid++;
        helper.log("userInfoManager.js", "getUidOrCreate()", `Assigned new UID ${newUid} to user ${username}`);
        return newUid;
    }

    /**
     * Checks if a username exists in the userMap
     * @param {string} username - The username to check
     * @returns {boolean} - True if the username exists, false otherwise
     */
    userExists(username) {
        return this.userMap[username] !== undefined;
    }

    /**
     * Gets the current user mappings
     * @returns {Object} - The current user to UID mappings
     */
    getUserMap() {
        return { ...this.userMap };
    }

    /**
     * Clean up resources
     * //Dineth: Added for proper test cleanup and resource management
     */
    cleanup() {
        this.userMap = {};
        this.nextUid = this.startUid;
    }
}

module.exports = UserInfoManager;
