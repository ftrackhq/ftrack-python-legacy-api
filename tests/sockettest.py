import ftrack

#setup the event listener
ftrack.setup()

def handleCallback(event, buttonId, userId, selection):
    
    if buttonId == 'my-custom-action':

        #create a job to inform the user that something is going on
        job = ftrack.createJob(description="My Custom Action", status="running", user=userId)

        try:

            for s in selection:

                version = ftrack.AssetVersion(s['entityId'])

                #DO SOMETHING WITH THE VERSION
                import time
                time.sleep(5)

            #inform the user that the action is done
            job.setStatus('done')

        except:

            #fail the job if something goes wrong
            job.setStatus('failed')
            raise

#subscribe to action
ftrack.EVENT_HUB.subscribe('action',handleCallback)
ftrack.EVENT_HUB.wait()