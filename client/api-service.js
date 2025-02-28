class ApiService {
    constructor() {
        this.baseUrl = 'http://localhost:5000';
    }

    // API methods
    async fetchApi(endpoint, options = {}) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            const response = await fetch(url, options);
            return await this.handleResponse(response);
        } catch (error) {
            return { error: error.message };
        }
    }

    async get(endpoint) {
        return this.fetchApi(endpoint);
    }

    async post(endpoint, data = {}) {
        return this.fetchApi(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
    }

    async delete(endpoint) {
        return this.fetchApi(endpoint, { method: 'DELETE' });
    }

    // System endpoints
    async getSystemInfo() {
        return this.get('/system/about');
    }

    async executeDirectCommand(command) {
        return this.post('/system/execute', { command });
    }

    // History endpoints
    async getAllChats() {
        return this.get('/history/chats');
    }

    async createNewChat() {
        return this.post('/history/chat');
    }

    async getChat(chatId) {
        return this.get(`/history/chat/${chatId}`);
    }

    async deleteChat(chatId) {
        return this.delete(`/history/chat/${chatId}`);
    }

    async addMessage(chatId, user, message) {
        return this.post(`/history/chat/${chatId}/message`, { user, message });
    }

    async updateChatContainer(chatId, containerId) {
        return this.post(`/history/chat/${chatId}/container`, { container_id: containerId });
    }

    // Sandbox endpoints
    async createContainer(image) {
        return this.get(`/sandbox/create/${image}`);
    }

    async startContainer(containerId) {
        return this.get(`/sandbox/start/${containerId}`);
    }

    async stopContainer(containerId) {
        return this.get(`/sandbox/stop/${containerId}`);
    }

    async pauseContainer(containerId) {
        return this.get(`/sandbox/pause/${containerId}`);
    }

    async unpauseContainer(containerId) {
        return this.get(`/sandbox/unpause/${containerId}`);
    }

    async removeContainer(containerId) {
        return this.delete(`/sandbox/remove/${containerId}`);
    }

    async listContainers() {
        return this.get('/sandbox/list');
    }

    async getContainerStatus(containerId) {
        return this.get(`/sandbox/status/${containerId}`);
    }

    async executeCommand(containerId, command) {
        return this.post(`/sandbox/execute/${containerId}`, { command });
    }

    async handleResponse(response) {
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || `HTTP error ${response.status}`);
        }
        
        try {
            const text = await response.text();
            return text ? JSON.parse(text) : {};
        } catch (error) {
            return response;
        }
    }
}

const apiService = new ApiService();
