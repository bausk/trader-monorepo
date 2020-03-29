export default async () => {
    try {
        let token = '';
        const res = await fetch('/api/gettoken');
        if (res.ok) {
            token = await res.json();
            const response = await fetch("http://localhost:5000/", {
                method: 'POST',
                headers: {
                Authorization: `Bearer ${token.accessToken}`
                },
            });
            const payload = await response.json()
            return JSON.stringify(payload);
        }
    } catch (e) {
        console.error(e);
        throw e;
    }
}
